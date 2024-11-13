import React, { useState } from 'react';
import { Box, Button, Typography } from '@mui/material';
import backgroundImage from '../assets/vr-bg-2.jpg';

function CsvUpload() {
    const [csvFile, setCsvFile] = useState(null);

    const handleFileChange = (event) => {
        setCsvFile(event.target.files[0]);
        console.log(event.target.files[0]);
    };

    const handleUpload = () => {
        if (csvFile) {
            // Handle the file upload logic here
            alert(`File ${csvFile.name} uploaded successfully!`);
        } else {
            alert("Please select a file first.");
        }
    };

    // Open file input dialog when button is clicked
    const handleButtonClick = () => {
        document.getElementById('file-input').click();
    };

    return (
        <Box
            sx={{
                height: '100vh',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                backgroundImage: `url(${backgroundImage})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
            }}
        >
            <Typography variant="h3" color="white" mb={2}>
                See True Technologies
            </Typography>

            {/* Hidden file input */}
            <input
                id="file-input"
                type="file"
                onChange={handleFileChange}
                accept=".csv"
                style={{ display: 'none' }}
            />

            {/* Styled button to trigger file input */}
            <Button
                variant="contained"
                color="primary"
                onClick={handleButtonClick}
                sx={{ mb: 2 }}
            >
                Choose CSV File
            </Button>

            {/* Show the selected file name */}
            {csvFile && (
                <Typography variant="body1" color="white" mb={2}>
                    Selected File: {csvFile.name}
                </Typography>
            )}

            <Button
                variant="contained"
                color="secondary"
                onClick={handleUpload}
                sx={{ mt: 2 }}
            >
                Upload
            </Button>
        </Box>
    );
}

export default CsvUpload;
