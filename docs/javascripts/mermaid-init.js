// Initialize Mermaid diagrams for ReadTheDocs theme
document.addEventListener('DOMContentLoaded', function() {
    mermaid.initialize({
        startOnLoad: true,
        theme: 'default',
        securityLevel: 'loose',
        flowchart: {
            useMaxWidth: true,
            htmlLabels: true,
            curve: 'basis'
        }
    });
    
    // Re-render any mermaid blocks that might have been missed
    mermaid.init(undefined, document.querySelectorAll('.mermaid'));
});
