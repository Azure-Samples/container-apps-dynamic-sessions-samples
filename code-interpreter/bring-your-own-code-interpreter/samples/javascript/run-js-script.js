var fs = require('fs');

// Read and execute the JavaScript file
fs.readFile('/mnt/data/sample-js-code.js', 'utf8', (err, data) => {
    if (err) {
        console.error('Error reading the file:', err);
        return;
    }
    
    try {
        eval(data); // Execute the JavaScript code from the file
        console.log('JavaScript code executed successfully');
    } catch (executionError) {
        console.error('Error executing the code:', executionError);
    }
});
