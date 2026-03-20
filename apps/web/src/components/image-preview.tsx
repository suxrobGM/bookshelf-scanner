"use client";

import {Card, CardContent, CardMedia, Typography, Stack} from "@mui/material";
import type { ReactElement } from "react";

interface ImagePreviewProps {
  uploadedSrc: string | null;
  segmentedSrc: string | null;
}

export function ImagePreview(props: ImagePreviewProps): ReactElement {
  const { uploadedSrc, segmentedSrc } = props;

  if (!uploadedSrc && !segmentedSrc) {return <></>;}

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
