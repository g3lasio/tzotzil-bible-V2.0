export interface SearchResult {
  reference: string;
  text: string;
  version: 'tzotzil' | 'spanish';
  book?: string;
  chapter?: number;
  verse?: number;
}

export interface SearchParams {
  keyword: string;
  versions: {
    tzotzil: boolean;
    spanish: boolean;
  };
  book: string;
}
