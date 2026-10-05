import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

/**
 * Avatar del usuario. AvatarImage cae solo al fallback si la imagen no carga,
 * asi que una foto rota nunca deja un hueco: quedan las iniciales.
 */
export function MemberAvatar({
  name,
  initials,
  photo,
  className,
  fallbackClassName,
}: {
  name: string;
  initials: string;
  photo?: string | null;
  className?: string;
  fallbackClassName?: string;
}) {
  return (
    <Avatar className={cn("size-8", className)}>
      {photo && <AvatarImage src={photo} alt="" className="object-cover" />}
      <AvatarFallback
        className={cn(
          "bg-accent text-xs font-semibold text-muted-foreground",
          fallbackClassName,
        )}
      >
        {initials}
      </AvatarFallback>
      <span className="sr-only">{name}</span>
    </Avatar>
  );
}
