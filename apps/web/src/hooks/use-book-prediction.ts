"use client";

import { type Result } from "@bookscanner/shared";
import { useRef, useState } from "react";
import { client } from "@/lib/api";

interface BookPredictionResult {
  results: string[];
  segmentedImage: string | null;
  error: string;
  isProcessing: boolean;
  predict: (file: File) => Promise<void>;
  cancel: () => void;
}

export function useBookPrediction(): BookPredictionResult {
  const [results, setResults] = useState<string[]>([]);
  const [segmentedImage, setSegmentedImage] = useState<string | null>(null);
  const [error, setError] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const predict = async (file: File) => {
    setIsProcessing(true);
    setResults([]);
    setSegmentedImage(null);
    setError("");

    abortRef.current = new AbortController();

    try {
      const { response } = await client.api.predict.post(
        { file },
        { fetch: { signal: abortRef.current.signal } },
      );

      if (!response.ok) {
        setError(`Server error: ${response.statusText}`);
        setIsProcessing(false);
        return;
      }

      const reader = response.body!.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";
      let isFirstResult = true;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;

          try {
            const data: Result<string> = JSON.parse(line);

            if (data.success && data.data) {
              if (isFirstResult) {
                setSegmentedImage(data.data);
                isFirstResult = false;
              } else {
                setResults((prev) => [...prev, data.data!]);
              }
            } else if (data.error) {
              setError(data.error);
            }
          } catch {
            setError("Error parsing response");
          }
        }
      }
    } catch (err) {
      if (abortRef.current?.signal.aborted) {
        setError("Process canceled by user.");
      } else {
        setError(err instanceof Error ? err.message : String(err));
      }
    } finally {
      setIsProcessing(false);
      abortRef.current = null;
    }
  };

  const cancel = () => {
    abortRef.current?.abort();
    abortRef.current = null;
  };

  return { results, segmentedImage, error, isProcessing, predict, cancel };
}
