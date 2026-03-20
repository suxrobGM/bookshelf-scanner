"use client";

import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";

interface ResultsListProps {
  results: string[];
}

export function ResultsList({ results }: ResultsListProps) {
  if (results.length === 0) return null;

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
