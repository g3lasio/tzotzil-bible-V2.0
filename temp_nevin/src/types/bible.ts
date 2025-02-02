
export interface BibleVerse {
  id: number;
  book: string;
  chapter: number;
  verse: number;
  tzotzil_text: string;
  spanish_text: string;
}

export interface BibleChapter {
  book: string;
  chapter: number;
  verses: BibleVerse[];
}

export interface SearchResult {
  verses: BibleVerse[];
  query: string;
  total: number;
}
