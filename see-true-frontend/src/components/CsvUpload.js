import React, { useState } from 'react';
import axios from 'axios';
import { Box, Button, Typography, CircularProgress } from '@mui/material';
import backgroundImage from '../assets/vr-bg-2.jpg';

function CsvUpload() {
    const [csvFile, setCsvFile] = useState(null);
    const [loading, setLoading] = useState(false); // State to manage loading

    const handleFileChange = (event) => {
        setCsvFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!csvFile) {
            alert("Please select a file first.");
            return;
        }

        setLoading(true); // Set loading to true when the request starts

        const formData = new FormData();
        formData.append("file", csvFile);

        try {
            // Make the POST request to the FastAPI backend
            const response = await axios.post("http://localhost:8000/classify", formData, {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            });

            // Handle the response from the backend
            console.log("Response from backend:", response.data);
            alert("File uploaded and processed successfully!");
        } catch (error) {
            console.error("Error uploading file:", error);
            alert("Failed to upload and process the file.");
        } finally {
            setLoading(false); // Set loading to false when the request completes
        }
    };

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
                disabled={loading}
            >
                Choose CSV File
            </Button>

            {/* Show the selected file name */}
            {csvFile && (
                <Typography variant="body1" color="white" mb={2}>
                    Selected File: {csvFile.name}
                </Typography>
            )}

            {/* Loader or Upload button */}
            {loading ? (
                <CircularProgress color="secondary" />
            ) : (
                <Button
                    variant="contained"
                    color="secondary"
                    onClick={handleUpload}
                    sx={{ mt: 2 }}
                >
                    Upload
                </Button>
            )}
        </Box>
    );
}

export default CsvUpload;
