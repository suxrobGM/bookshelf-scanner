"use client";

import { useRef } from "react";
import Button from "@mui/material/Button";
import Stack from "@mui/material/Stack";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import CancelIcon from "@mui/icons-material/Cancel";

interface UploadFormProps {
  isProcessing: boolean;
  onFileSelected: (file: File) => void;
  onSubmit: () => void;
  onCancel: () => void;
  hasFile: boolean;
}

export function UploadForm({
  isProcessing,
  onFileSelected,
  onSubmit,
  onCancel,
  hasFile,
}: UploadFormProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelected(file);
  };

  return (
    <Stack direction="row" spacing={2} alignItems="center">
      <Button variant="outlined" component="label">
        Choose Image
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          hidden
          onChange={handleChange}
        />
      </Button>

      <Button
        variant="contained"
        startIcon={<CloudUploadIcon />}
        disabled={!hasFile || isProcessing}
        onClick={onSubmit}
      >
        Upload
      </Button>

      <Button
        variant="outlined"
        color="error"
        startIcon={<CancelIcon />}
        disabled={!isProcessing}
        onClick={onCancel}
      >
        Cancel
      </Button>
    </Stack>
  );
}
