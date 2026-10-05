import { AlertCircle, LogIn } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type Props = {
  csrfToken: string;
  /** Errores que ya devolvio Django tras un intento fallido. */
  errors: string[];
  email: string;
  logoUrl: string;
};

export default function Login({ csrfToken, errors, email, logoUrl }: Props) {
  return (
    <div className="flex min-h-svh w-full items-center justify-center bg-muted p-6">
      <div className="flex w-full max-w-sm flex-col gap-6">
        <div className="flex items-center justify-center gap-2 self-center text-lg font-semibold text-foreground">
          <div className="flex size-10 items-center justify-center rounded-lg bg-white p-1.5 ring-1 ring-border">
            <img src={logoUrl} alt="" className="size-full object-contain" />
          </div>
          Neural Manager
        </div>

        <Card>
          <CardHeader className="text-center">
            <CardTitle className="text-xl">Bienvenido</CardTitle>
            <CardDescription>Ingresa con tu cuenta de administrador</CardDescription>
          </CardHeader>
          <CardContent>
            {errors.length > 0 && (
              <div
                role="alert"
                className="mb-6 flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive"
              >
                <AlertCircle className="mt-0.5 size-4 flex-none" />
                <span>{errors[0]}</span>
              </div>
            )}

            <form method="post" className="grid gap-5">
              <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />

              <div className="grid gap-2">
                <Label htmlFor="id_email">Email</Label>
                <Input
                  id="id_email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  defaultValue={email}
                  placeholder="admin@neural.com.co"
                  required
                  autoFocus
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="id_password">Contraseña</Label>
                <Input
                  id="id_password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                />
              </div>

              <Button type="submit" className="w-full">
                <LogIn className="size-4" />
                Iniciar sesión
              </Button>
            </form>
          </CardContent>
        </Card>

        <p className="text-center text-xs text-muted-foreground">
          Panel interno de Neural Consciente
        </p>
      </div>
    </div>
  );
}
