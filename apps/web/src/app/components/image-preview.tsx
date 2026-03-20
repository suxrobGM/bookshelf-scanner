"use client";

import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardMedia from "@mui/material/CardMedia";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";

interface ImagePreviewProps {
  uploadedSrc: string | null;
  segmentedSrc: string | null;
}

export function ImagePreview({ uploadedSrc, segmentedSrc }: ImagePreviewProps) {
  if (!uploadedSrc && !segmentedSrc) return null;

  return (
    <Stack direction="row" spacing={2} flexWrap="wrap" justifyContent="center">
      {uploadedSrc && (
        <Card sx={{ maxWidth: 600 }}>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Uploaded Image
            </Typography>
          </CardContent>
          <CardMedia
            component="img"
            image={uploadedSrc}
            alt="Uploaded image preview"
            sx={{ maxHeight: 500, objectFit: "contain" }}
          />
        </Card>
      )}

      {segmentedSrc && (
        <Card sx={{ maxWidth: 600 }}>
          <CardContent>
            <Typography variant="subtitle1" gutterBottom>
              Segmented Image
            </Typography>
          </CardContent>
          <CardMedia
            component="img"
            image={segmentedSrc}
            alt="Segmented image with detected books"
            sx={{ maxHeight: 500, objectFit: "contain" }}
          />
        </Card>
      )}
    </Stack>
  );
}
