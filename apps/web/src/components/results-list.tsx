"use client";

import type { ReactElement } from "react";
import { List, ListItem, ListItemText, Paper, Typography } from "@mui/material";

interface ResultsListProps {
  results: string[];
}

export function ResultsList(props: ResultsListProps): ReactElement {
  const { results } = props;

  if (results.length === 0) {
    return <></>;
  }

  return (
    <Paper variant="outlined" sx={{ maxHeight: 400, overflow: "auto", width: "100%" }}>
      <Typography variant="subtitle1" sx={{ p: 2, pb: 0 }}>
        Recognized Books
      </Typography>
      <List dense>
        {results.map((result, index) => (
          <ListItem key={index}>
            <ListItemText primary={result} />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
}
