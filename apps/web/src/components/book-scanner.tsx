"use client";

import { useState, type ReactElement } from "react";
import { Alert, Container, LinearProgress, Stack, Typography } from "@mui/material";
import { useBookPrediction } from "@/hooks/use-book-prediction";
import { ImagePreview } from "./image-preview";
import { ResultsList } from "./results-list";
import { UploadForm } from "./upload-form";

export function BookScanner(): ReactElement {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadedImageSrc, setUploadedImageSrc] = useState<string | null>(null);
  const { results, segmentedImage, error, isProcessing, predict, cancel } = useBookPrediction();

  const handleFileSelected = (file: File) => {
    setSelectedFile(file);

    const reader = new FileReader();
    reader.onload = () => setUploadedImageSrc(reader.result as string);
    reader.readAsDataURL(file);
  };

  const handleSubmit = () => {
    if (selectedFile) predict(selectedFile);
  };

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

        <ImagePreview uploadedSrc={uploadedImageSrc} segmentedSrc={segmentedImage} />
      </Stack>
    </Container>
  );
}
