// tools-panel.js - Manages the Strands tools selection side panel

// Initialize the tools panel
async function initToolsPanel() {
    const toolsPanel = document.getElementById('tools-panel');
    if (!toolsPanel) return;

    // Fetch current tools configuration
    try {
        const response = await fetch('/get_available_tools');
        const data = await response.json();
        
        if (data.available_tools && data.selected_tools) {
            renderEnabledTools(toolsPanel, data.selected_tools, data.tool_descriptions || {});
        }
    } catch (error) {
        console.error('Error fetching tools:', error);
        const errorP = document.createElement('p');
        errorP.className = 'error';
        errorP.textContent = 'Failed to load tools';
        toolsPanel.appendChild(errorP);
    }
}

// Render enabled tools only (no checkboxes / no update)
function renderEnabledTools(container, enabledTools, toolDescriptions = {}) {
    container.textContent = '';

    // Header
    const header = document.createElement('div');
    header.className = 'tools-panel-header';
    const h3 = document.createElement('h3');
    h3.textContent = 'Enabled Tools';
    header.appendChild(h3);

    // Tools list
    const toolsList = document.createElement('div');
    toolsList.className = 'tools-list';

    enabledTools.forEach(tool => {
        const toolItem = document.createElement('div');
        toolItem.className = 'tool-item';

        const name = document.createElement('div');
        name.className = 'tool-name';
        name.textContent = tool;

        const description = document.createElement('p');
        description.className = 'tool-description';
        description.textContent = toolDescriptions[tool] || 'No description available';

        toolItem.appendChild(name);
        toolItem.appendChild(description);
        toolsList.appendChild(toolItem);
    });

    container.appendChild(header);
    container.appendChild(toolsList);
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }, 100);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initToolsPanel);