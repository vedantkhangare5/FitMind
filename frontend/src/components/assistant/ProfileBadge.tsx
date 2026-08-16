import { User } from "lucide-react";

interface ProfileBadgeProps {
  profileUsed: boolean;
}

export function ProfileBadge({ profileUsed }: ProfileBadgeProps) {
  if (!profileUsed) return null;

  return (
    <div className="flex items-center gap-1.5 mb-3 px-3 py-1.5 rounded-full bg-violet-50 dark:bg-violet-950/30 border border-violet-200 dark:border-violet-800/30 w-fit">
      <User className="w-3.5 h-3.5 text-violet-600 dark:text-violet-400" />
      <span className="text-xs font-medium text-violet-600 dark:text-violet-400">
        Using your saved fitness profile
      </span>
    </div>
  );
}
