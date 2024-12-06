import React, { useState, useEffect } from "react";
import axios from "axios";
import { Box, Button, Typography, CircularProgress } from "@mui/material";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import backgroundImage from "../assets/vr-bg-2.jpg";

function CsvLiveActivity() {
    const [csvFile, setCsvFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [polling, setPolling] = useState(false);
    const [currentActivity, setCurrentActivity] = useState("N/A");
    const [finalActivity, setFinalActivity] = useState(null);
    const [resultsKey, setResultsKey] = useState(null);
    const [batchResults, setBatchResults] = useState([]);

    const labelMap = {
        walking: "Walking",
        reading: "Reading",
        playing: "Playing",
    };

    const handleFileChange = (event) => {
        setCsvFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!csvFile) {
            toast.error("Please select a file first.");
            return;
        }

        setLoading(true);
        setResultsKey(null);
        setFinalActivity(null);
        setBatchResults([]);

        const formData = new FormData();
        formData.append("file", csvFile);

        try {
            const response = await axios.post("http://localhost:8000/classify_in_batches", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            setResultsKey(response.data.key);
            toast.success("File uploaded successfully. Processing started!");
        } catch (error) {
            console.error("Error uploading file:", error);
            toast.error("Failed to upload and process the file.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (resultsKey) {
            setPolling(true);

            const interval = setInterval(async () => {
                try {
                    const response = await axios.get(`http://localhost:8000/results/${resultsKey}`);
                    const resultData = response.data;

                    if (resultData.batches?.length > 0) {
                        const latestBatch = resultData.batches[resultData.batches.length - 1];
                        setCurrentActivity(labelMap[latestBatch.highest_class]);
                        setBatchResults((prev) => [...prev, latestBatch]);
                    }

                    if (resultData.status === "complete") {
                        clearInterval(interval);
                        setPolling(false);
                        setFinalActivity(resultData.final_result.final_activity); // Correctly set final activity
                        toast.success(`Processing complete! Final Activity: ${resultData.final_result.final_activity}`);
                    }
                } catch (error) {
                    console.error("Error fetching results:", error);
                    toast.error("Error fetching results. Stopping polling.");
                    clearInterval(interval);
                    setPolling(false);
                }
            }, 10000);

            return () => clearInterval(interval);
        }
    }, [resultsKey]);

    const handleButtonClick = () => {
        document.getElementById("file-input").click();
    };

    return (
        <Box
            sx={{
                minHeight: "100vh",
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                backgroundImage: `url(${backgroundImage})`,
                backgroundSize: "cover",
                backgroundPosition: "center",
                padding: 4,
                color: "white",
                overflow: "auto",
            }}
        >
            <Typography variant="h3" color="white" mb={2}>
                See True
            </Typography>

            <input
                id="file-input"
                type="file"
                onChange={handleFileChange}
                accept=".csv"
                style={{ display: "none" }}
            />

            <Button
                variant="contained"
                color="primary"
                onClick={handleButtonClick}
                sx={{ mb: 2 }}
                disabled={loading || polling}
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
                    disabled={loading || polling}
                >
                    Upload
                </Button>
            )}

            {polling && (
                <>
                    <Box sx={{ mt: 2, textAlign: "left" }}>
                        {batchResults.map((batch, index) => (
                            <Typography key={index} variant="body2" color="lightgray">
                                Batch {index + 1}: {labelMap[batch.highest_class]} ({JSON.stringify(batch.means)})
                            </Typography>
                        ))}
                    </Box>
                </>
            )}

            {finalActivity && (
                <Typography variant="h4" color="lime" mt={4}>
                    Final Activity: {finalActivity}
                </Typography>
            )}

            <ToastContainer />
        </Box>
    );
}

export default CsvLiveActivity;
