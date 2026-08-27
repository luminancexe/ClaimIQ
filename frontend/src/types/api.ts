export interface PaginatedResponse<T> {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
  items: T[];
}

export interface ErrorResponse {
  error_code: string;
  message: string;
  request_id?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  database_connected: boolean;
  timestamp: string;
}

export interface ApiPaginationParams {
  page?: number;
  page_size?: number;
}

export interface ColumnDef<T> {
  key: string;
  header: React.ReactNode;
  cell?: (row: T, index: number) => React.ReactNode;
  className?: string;
  headerClassName?: string;
  align?: 'left' | 'center' | 'right';
}

