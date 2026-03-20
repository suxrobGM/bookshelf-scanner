"use client";

import { useState, useCallback } from "react";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";
import Alert from "@mui/material/Alert";
import LinearProgress from "@mui/material/LinearProgress";
import { UploadForm } from "./upload-form";
import { ImagePreview } from "./image-preview";
import { ResultsList } from "./results-list";
import { useBookPrediction } from "../hooks/use-book-prediction";

export function BookScanner() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadedImageSrc, setUploadedImageSrc] = useState<string | null>(null);
  const { results, segmentedImage, error, isProcessing, predict, cancel } =
    useBookPrediction();

  const handleFileSelected = useCallback((file: File) => {
    setSelectedFile(file);

    const reader = new FileReader();
    reader.onload = () => setUploadedImageSrc(reader.result as string);
    reader.readAsDataURL(file);
  }, []);

  const handleSubmit = useCallback(() => {
    if (selectedFile) predict(selectedFile);
  }, [selectedFile, predict]);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Stack spacing={3} alignItems="center">
        <Typography variant="h3" component="h1">
          Book Recognizer
        </Typography>

        <UploadForm
          isProcessing={isProcessing}
          onFileSelected={handleFileSelected}
          onSubmit={handleSubmit}
          onCancel={cancel}
          hasFile={selectedFile !== null}
        />

        {isProcessing && (
          <Stack spacing={1} sx={{ width: "100%" }}>
            <Typography variant="body2" color="text.secondary">
              Processing image...
            </Typography>
            <LinearProgress />
          </Stack>
        )}

        {error && (
          <Alert severity="error" sx={{ width: "100%" }}>
            {error}
          </Alert>
        )}

        <ResultsList results={results} />

        <ImagePreview
          uploadedSrc={uploadedImageSrc}
          segmentedSrc={segmentedImage}
        />
      </Stack>
    </Container>
  );
}
