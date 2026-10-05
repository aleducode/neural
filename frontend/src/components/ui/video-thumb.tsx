import { Play, Video as VideoIcon } from "lucide-react";

import { cn } from "@/lib/utils";

/**
 * Miniatura de un video. La de YouTube la genera YouTube; la de un archivo
 * subido hay que cargarla a mano, así que cuando no hay va un marcador en vez
 * de un hueco.
 */
export function VideoThumb({
  poster,
  name,
  className,
}: {
  poster?: string | null;
  name: string;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "relative flex h-12 w-20 flex-none items-center justify-center overflow-hidden rounded-md bg-secondary",
        className,
      )}
    >
      {poster ? (
        <>
          <img src={poster} alt="" className="size-full object-cover" />
          <span className="absolute inset-0 flex items-center justify-center bg-foreground/20">
            <Play className="size-4 fill-white text-white" aria-hidden="true" />
          </span>
        </>
      ) : (
        <VideoIcon className="size-4 text-faint" aria-hidden="true" />
      )}
      <span className="sr-only">{name}</span>
    </span>
  );
}
