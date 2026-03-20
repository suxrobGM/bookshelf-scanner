export type SortOrder = "asc" | "desc";

export interface PaginationQuery {
  page?: number;
  limit?: number;
}

export interface PaginationResult<T = unknown> {
  items: T[];
  pagination: PaginationInfo;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}
