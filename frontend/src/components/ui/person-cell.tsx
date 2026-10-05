import { MemberAvatar } from "@/components/ui/member-avatar";
import { TableCell } from "@/components/ui/table";

/**
 * Celda «Member Name» del .pen: avatar de 32, nombre 14/500 y una segunda
 * linea en 12 con el identificador. El diseno pone ahi un codigo «MB-00124»;
 * Neural no lo tiene, asi que va el email, que es su identificador real.
 */
export function PersonCell({
  name,
  initials,
  photo,
  sub,
  href,
}: {
  name: string;
  initials: string;
  photo?: string | null;
  sub: string;
  href?: string;
}) {
  const inner = (
    <>
      <MemberAvatar name={name} initials={initials} photo={photo} />
      <span className="min-w-0">
        <span className="block truncate text-sm font-medium text-foreground">{name}</span>
        <span className="block truncate text-xs text-muted-foreground">{sub}</span>
      </span>
    </>
  );

  return (
    <TableCell>
      {href ? (
        <a href={href} className="flex items-center gap-2.5 no-underline">
          {inner}
        </a>
      ) : (
        <span className="flex items-center gap-2.5">{inner}</span>
      )}
    </TableCell>
  );
}
