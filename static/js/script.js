document.addEventListener('DOMContentLoaded', function () {
    // Clear file inputs
    document.getElementById('singleFileInput').value = '';
    document.getElementById('projectFolder').value = '';

    // Clear text input
    document.getElementById('codeInput').value = '';
});

document.getElementById('analyzeCodeButton').addEventListener('click', async function () {
    const codeSnippet = document.getElementById('codeInput').value.trim();

    if (!codeSnippet) {
        alert("Please enter code to analyze.");
        return;
    }

    // Show the loader
    document.getElementById('loader').style.display = 'block';

    const formData = new FormData();
    formData.append('codeSnippet', codeSnippet);

    try {
        const response = await fetch('/analyze_snippet', {
            method: 'POST',
            body: formData
        });

        const reportData = await response.json();
        displayResults(reportData);
    } catch (error) {
        console.error("Error analyzing code snippet:", error);
    } finally {
        document.getElementById('loader').style.display = 'none';
    }
});

// Analyze Single Python File
document.getElementById('analyzeFileButton').addEventListener('click', async function () {
    const singleFileInput = document.getElementById('singleFileInput').files[0];

    if (!singleFileInput) {
        alert("Please select a Python file to analyze.");
        return;
    }

    // Show the loader
    document.getElementById('loader').style.display = 'block';

    const formData = new FormData();
    formData.append('file', singleFileInput);

    try {
        const response = await fetch('/analyze_file', {
            method: 'POST',
            body: formData
        });

        const reportData = await response.json();
        displayResults(reportData);
    } catch (error) {
        console.error("Error analyzing file:", error);
    } finally {
        document.getElementById('loader').style.display = 'none';
    }
});

// Analyze Project Folder
document.getElementById('scanButton').addEventListener('click', async function() {
    const projectFolder = document.getElementById('projectFolder').files;
    
    if (!projectFolder.length) {
        alert("Please select a project folder to scan.");
        return;
    }

    // Show the loader
    document.getElementById('loader').style.display = 'block';

    const formData = new FormData();
    formData.append('projectFolder', projectFolder[0].webkitRelativePath.split('/')[0]);

    try {
        const response = await fetch('/scan', {
            method: 'POST',
            body: formData
        });

        const reportData = await response.json();
        displayResults(reportData);
    } catch (error) {
        console.error("Error during scan:", error);
    } finally {
        // Hide the loader after the scan is finished
        document.getElementById('loader').style.display = 'none';
    }
});

// Download PDF Report
document.getElementById('downloadPDFButton').addEventListener('click', function () {
    window.location.href = '/download_pdf';
});

// Display Results in Chart
function displayResults(data) {
    // Summarize code smells by type
    const smellCounts = data.reduce((acc, item) => {
        acc[item.code_smell] = (acc[item.code_smell] || 0) + 1;
        return acc;
    }, {});

    // Get the chart container
    const ctx = document.getElementById('chart').getContext('2d');

    // Clear any existing chart before creating a new one
    if (window.smellChart) {
        window.smellChart.destroy();
    }

    // Create a bar chart with the summarized data
    window.smellChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(smellCounts),
            datasets: [{
                label: 'Code Smells Count',
                data: Object.values(smellCounts),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)',
                    'rgba(255, 159, 64, 0.6)',
                    'rgba(201, 203, 207, 0.6)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(201, 203, 207, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Summary of Code Smells'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Display total number of code smells in a beautiful way
    const totalSmellsContainer = document.getElementById('totalSmells');
    totalSmellsContainer.innerHTML = '';  // Clear existing content

    // Create and append a total count display for each code smell
    Object.keys(smellCounts).forEach(smell => {
        const count = smellCounts[smell];

        // Create a card or badge for each code smell
        const smellCard = document.createElement('div');
        smellCard.classList.add('smell-card');
        smellCard.innerHTML = `
            <h3>${smell}</h3>
            <p>Total: <strong>${count}</strong></p>
        `;

        totalSmellsContainer.appendChild(smellCard);
    });
}
