import React, { useState } from 'react';
import axios from 'axios';
import { Box, Button, Typography, CircularProgress, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, TablePagination } from '@mui/material';
import backgroundImage from '../assets/vr-bg-2.jpg';

function CsvUpload() {
    const [csvFile, setCsvFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [predictions, setPredictions] = useState([]);
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);

    const handleFileChange = (event) => {
        setCsvFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!csvFile) {
            alert("Please select a file first.");
            return;
        }

        setLoading(true);
        setPredictions([]);

        const formData = new FormData();
        formData.append("file", csvFile);

        try {
            const response = await axios.post("http://localhost:8000/classify", formData, {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            });

            setPredictions(response.data.predictions);
            alert("File uploaded and processed successfully!");
        } catch (error) {
            console.error("Error uploading file:", error);
            alert("Failed to upload and process the file.");
        } finally {
            setLoading(false);
        }
    };

    const handleButtonClick = () => {
        document.getElementById('file-input').click();
    };

    // Handle page change
    const handleChangePage = (event, newPage) => {
        setPage(newPage);
    };

    // Handle rows per page change
    const handleChangeRowsPerPage = (event) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0); // Reset to the first page
    };

    // Calculate the data to display on the current page
    const paginatedData = predictions.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

    return (
        <Box
            sx={{
                minHeight: '100vh',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                backgroundImage: `url(${backgroundImage})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                padding: 4,
                color: 'white',
                overflow: 'auto',
            }}
        >
            <Typography variant="h3" color="white" mb={2}>
                See True Technologies
            </Typography>

            <input
                id="file-input"
                type="file"
                onChange={handleFileChange}
                accept=".csv"
                style={{ display: 'none' }}
            />

            <Button
                variant="contained"
                color="primary"
                onClick={handleButtonClick}
                sx={{ mb: 2 }}
                disabled={loading}
            >
                Choose CSV File
            </Button>

            {csvFile && (
                <Typography variant="body1" color="white" mb={2}>
                    Selected File: {csvFile.name}
                </Typography>
            )}

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

            {predictions.length > 0 && (
                <Box
                    sx={{
                        mt: 4,
                        maxWidth: '80%',
                        backgroundColor: 'white',
                        color: 'black',
                        borderRadius: '8px',
                        overflow: 'hidden',
                    }}
                >
                    <TableContainer component={Paper}>
                        <Table>
                            <TableHead>
                                <TableRow>
                                    <TableCell>Prediction Index</TableCell>
                                    <TableCell>Predictions</TableCell>
                                    <TableCell>Label Classes</TableCell>
                                    <TableCell>Prev Euclidean Distance</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {paginatedData.map((prediction, index) => (
                                    <TableRow key={index}>
                                        <TableCell>{page * rowsPerPage + index + 1}</TableCell>
                                        <TableCell>{prediction.predictions.join(", ")}</TableCell>
                                        <TableCell>{prediction.label_classes.join(", ")}</TableCell>
                                        <TableCell>{prediction.prev_euclidean_distance ?? "N/A"}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                    <TablePagination
                        rowsPerPageOptions={[10, 25, 50]}
                        component="div"
                        count={predictions.length}
                        rowsPerPage={rowsPerPage}
                        page={page}
                        onPageChange={handleChangePage}
                        onRowsPerPageChange={handleChangeRowsPerPage}
                    />
                </Box>
            )}
        </Box>
    );
}

export default CsvUpload;
