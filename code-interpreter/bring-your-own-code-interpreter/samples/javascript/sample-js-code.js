var fs = require('fs'); // Node.js file system module
var { promisify } = require('util');
var writeFile = promisify(fs.writeFile);

async function fetchAndProcessData(url, outputFilePath) {
    try {
        // Step 1: Download the JSON data
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch data: ${response.statusText}`);
        }

        // Step 2: Parse the JSON data
        const data = await response.json();

        // Step 3: Manipulate the data (filter users by email)
        const filteredData = data.filter(user => user.email.includes('@'));

        // Step 4: Save the manipulated data to a new file
        await writeFile(outputFilePath, JSON.stringify(filteredData, null, 2));
        console.log(`Data downloaded and processed. Saved to: ${outputFilePath}`);
    } catch (error) {
        console.error(`Error: ${error.message}`);
    }
}

// Usage example
var apiUrl = 'https://jsonplaceholder.typicode.com/users'; // Replace with the actual API URL
var outputFilePath = '/mnt/data/filtered_users.json'; // Specify the path where you want to save the manipulated file

fetchAndProcessData(apiUrl, outputFilePath);
