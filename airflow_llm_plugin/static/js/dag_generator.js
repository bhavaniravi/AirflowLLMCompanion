document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const dagGeneratorForm = document.getElementById('dag-generator-form');
    const promptNameInput = document.getElementById('prompt-name');
    const promptDescriptionInput = document.getElementById('prompt-description');
    const promptTextInput = document.getElementById('prompt-text');
    const generateDagBtn = document.getElementById('generate-dag-btn');
    const generationResult = document.getElementById('generation-result');
    const dagIdDisplay = document.getElementById('dag-id-display');
    const promptsContainer = document.getElementById('prompts-container');
    const refreshPromptsBtn = document.getElementById('refresh-prompts-btn');
    
    // Current prompt ID (set when a prompt is saved or selected)
    let currentPromptId = null;
    
    // Function to load saved prompts
    function loadPrompts() {
        fetch('/api/dag/prompts')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayPrompts(data.prompts);
                } else {
                    promptsContainer.innerHTML = `
                        <div class="alert alert-danger">
                            Error loading prompts: ${data.error || 'Unknown error'}
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error loading prompts:', error);
                promptsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        Error loading prompts. Please try refreshing the page.
                    </div>
                `;
            });
    }
    
    // Function to display prompts
    function displayPrompts(prompts) {
        if (prompts.length === 0) {
            promptsContainer.innerHTML = `
                <div class="text-center text-muted">
                    <p>No prompts saved yet. Create your first prompt above!</p>
                </div>
            `;
            return;
        }
        
        let html = '<div class="table-responsive"><table class="table table-hover">';
        html += `
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>DAG Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
        `;
        
        prompts.forEach(prompt => {
            html += `
                <tr data-prompt-id="${prompt.id}">
                    <td>${prompt.name}</td>
                    <td>${prompt.description || '<em>No description</em>'}</td>
                    <td>
                        ${prompt.dag_id ? 
                            `<span class="badge bg-success">Generated (${prompt.dag_id})</span>` : 
                            '<span class="badge bg-secondary">Not generated</span>'}
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary load-prompt-btn" data-prompt-id="${prompt.id}">
                                <i class="fas fa-edit"></i>
                            </button>
                            ${!prompt.dag_id ? 
                                `<button class="btn btn-outline-success generate-prompt-btn" data-prompt-id="${prompt.id}">
                                    <i class="fas fa-cogs"></i>
                                </button>` : ''}
                            <button class="btn btn-outline-danger delete-prompt-btn" data-prompt-id="${prompt.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
        promptsContainer.innerHTML = html;
        
        // Add event listeners to the buttons
        document.querySelectorAll('.load-prompt-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const promptId = this.getAttribute('data-prompt-id');
                loadPromptDetails(promptId, prompts);
            });
        });
        
        document.querySelectorAll('.generate-prompt-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const promptId = this.getAttribute('data-prompt-id');
                generateDag(promptId);
            });
        });
        
        document.querySelectorAll('.delete-prompt-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const promptId = this.getAttribute('data-prompt-id');
                deletePrompt(promptId);
            });
        });
    }
    
    // Function to load prompt details for editing
    function loadPromptDetails(promptId, prompts) {
        const prompt = prompts.find(p => p.id.toString() === promptId.toString());
        if (!prompt) return;
        
        promptNameInput.value = prompt.name;
        promptDescriptionInput.value = prompt.description || '';
        promptTextInput.value = prompt.prompt;
        
        currentPromptId = prompt.id;
        
        // Show generate button if this prompt hasn't been generated yet
        if (!prompt.dag_id) {
            generateDagBtn.classList.remove('d-none');
            generateDagBtn.setAttribute('data-prompt-id', prompt.id);
        } else {
            generateDagBtn.classList.add('d-none');
            
            // Show success message with DAG ID
            generationResult.classList.remove('d-none');
            dagIdDisplay.textContent = `DAG ID: ${prompt.dag_id}`;
        }
        
        // Scroll to the form
        dagGeneratorForm.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Function to save a prompt
    function savePrompt(name, description, promptText) {
        fetch('/api/dag/prompts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                description: description,
                prompt: promptText
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Set the current prompt ID
                currentPromptId = data.prompt_id;
                
                // Show the generate button
                generateDagBtn.classList.remove('d-none');
                generateDagBtn.setAttribute('data-prompt-id', data.prompt_id);
                
                // Hide any previous generation result
                generationResult.classList.add('d-none');
                
                // Reload prompts
                loadPrompts();
                
                // Show success message
                alert('Prompt saved successfully!');
            } else {
                alert(`Error saving prompt: ${data.error || 'Unknown error'}`);
            }
        })
        .catch(error => {
            console.error('Error saving prompt:', error);
            alert('Error saving prompt. Please try again.');
        });
    }
    
    // Function to generate a DAG from a prompt
    function generateDag(promptId) {
        if (!confirm('Are you sure you want to generate a DAG from this prompt?')) {
            return;
        }
        
        // Show loading state
        const btn = document.querySelector(`.generate-prompt-btn[data-prompt-id="${promptId}"]`) || generateDagBtn;
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        btn.disabled = true;
        
        fetch(`/api/dag/generate/${promptId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            // Reset button state
            btn.innerHTML = originalHtml;
            btn.disabled = false;
            
            if (data.success) {
                // Show success message
                generationResult.classList.remove('d-none');
                dagIdDisplay.textContent = `DAG ID: ${data.dag_id}`;
                
                // Hide generate button
                generateDagBtn.classList.add('d-none');
                
                // Reload prompts
                loadPrompts();
                
                // Show success alert
                alert(`DAG generated successfully! DAG ID: ${data.dag_id}`);
            } else {
                alert(`Error generating DAG: ${data.error || 'Unknown error'}`);
            }
        })
        .catch(error => {
            // Reset button state
            btn.innerHTML = originalHtml;
            btn.disabled = false;
            
            console.error('Error generating DAG:', error);
            alert('Error generating DAG. Please try again.');
        });
    }
    
    // Function to delete a prompt
    function deletePrompt(promptId) {
        if (!confirm('Are you sure you want to delete this prompt?')) {
            return;
        }
        
        fetch(`/api/dag/prompts/${promptId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // If the deleted prompt was the current one, reset the form
                if (currentPromptId === promptId) {
                    promptNameInput.value = '';
                    promptDescriptionInput.value = '';
                    promptTextInput.value = '';
                    currentPromptId = null;
                    generateDagBtn.classList.add('d-none');
                    generationResult.classList.add('d-none');
                }
                
                // Reload prompts
                loadPrompts();
                
                // Show success message
                alert('Prompt deleted successfully!');
            } else {
                alert(`Error deleting prompt: ${data.error || 'Unknown error'}`);
            }
        })
        .catch(error => {
            console.error('Error deleting prompt:', error);
            alert('Error deleting prompt. Please try again.');
        });
    }
    
    // Event listeners
    dagGeneratorForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const name = promptNameInput.value.trim();
        const description = promptDescriptionInput.value.trim();
        const promptText = promptTextInput.value.trim();
        
        if (!name || !promptText) {
            alert('Please fill in all required fields.');
            return;
        }
        
        savePrompt(name, description, promptText);
    });
    
    generateDagBtn.addEventListener('click', function() {
        const promptId = this.getAttribute('data-prompt-id');
        generateDag(promptId);
    });
    
    refreshPromptsBtn.addEventListener('click', function() {
        loadPrompts();
    });
    
    // Load prompts on page load
    loadPrompts();
});
