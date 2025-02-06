
export interface Book {
  id: number;
  name: string;
  book_number: number;
  testament: string;
}

export interface Chapter {
  id: number;
  book_id: number;
  chapter_number: number;
  verses_count: number;
}

export interface BibleVerse {
  id: number;
  book_id: number;
  chapter: number;
  verse: number;
  text: string;
  text_tzotzil?: string;
  book_name?: string;
}

export interface SearchResult {
  verses: BibleVerse[];
  total: number;
  query: string;
}
