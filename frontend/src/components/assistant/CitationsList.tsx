import { ExternalLink } from "lucide-react";

export interface Citation {
  document_id: string;
  title: string;
  source_name: string;
  source_url?: string | null;
  section?: string | null;
  page?: string | null;
  text_type: string;
}

interface CitationsListProps {
  citations: Citation[];
}

export function CitationsList({ citations }: CitationsListProps) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-4 pt-4 border-t border-zinc-200 dark:border-zinc-800">
      <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">
        Verified Sources
      </h4>
      <div className="grid gap-2 sm:grid-cols-2">
        {citations.map((citation) => {
          const content = (
            <>
              <div className="font-medium text-sm text-zinc-900 dark:text-zinc-100 truncate">
                {citation.title}
              </div>
              <div className="text-xs text-zinc-500 dark:text-zinc-400 mt-1 flex items-center justify-between">
                <span className="truncate">{citation.source_name}</span>
                {citation.source_url && (
                  <ExternalLink className="w-3 h-3 ml-1 flex-shrink-0" />
                )}
              </div>
              {(citation.section || citation.page) && (
                <div className="text-xs text-zinc-400 dark:text-zinc-500 mt-1">
                  {citation.section && <span>Sec: {citation.section} </span>}
                  {citation.page && <span>Pg: {citation.page}</span>}
                </div>
              )}
            </>
          );

          if (citation.source_url) {
            return (
              <a
                key={citation.document_id}
                href={citation.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-3 rounded-lg border border-zinc-200 bg-zinc-50 hover:bg-zinc-100 hover:border-zinc-300 dark:border-zinc-800 dark:bg-zinc-900/50 dark:hover:bg-zinc-800/80 transition-colors"
              >
                {content}
              </a>
            );
          }

          return (
            <div
              key={citation.document_id}
              className="p-3 rounded-lg border border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900/50"
            >
              {content}
            </div>
          );
        })}
      </div>
    </div>
  );
}
