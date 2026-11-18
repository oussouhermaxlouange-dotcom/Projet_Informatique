<?php
declare(strict_types=1);

namespace App\Support;

/**
 * Routeur très simple : méthodes HTTP, chemins fixes et paramètres {nom}.
 * Aucune dépendance externe.
 */
final class Router
{
    /** @var list<array{method: string, regex: string, handler: callable}> */
    private array $routes = [];

    public function add(string $method, string $path, callable $handler): void
    {
        $motif = preg_replace('#\{([a-zA-Z_][a-zA-Z0-9_]*)\}#', '(?P<$1>[^/]+)', $path);

        $this->routes[] = [
            'method' => strtoupper($method),
            'regex' => '#^' . $motif . '$#',
            'handler' => $handler,
        ];
    }

    public function dispatch(Request $requete): Response
    {
        $method = strtoupper($requete->methode);
        $path = rtrim($requete->chemin, '/');
        if ($path === '') {
            $path = '/';
        }

        $cheminConnu = false;

        foreach ($this->routes as $route) {
            if (preg_match($route['regex'], $path, $correspondances) !== 1) {
                continue;
            }

            $cheminConnu = true;

            if ($route['method'] !== $method) {
                continue;
            }

            $parametres = array_filter(
                $correspondances,
                static fn (int|string $cle): bool => is_string($cle),
                ARRAY_FILTER_USE_KEY
            );

            return ($route['handler'])($parametres, $requete);
        }

        if ($cheminConnu) {
            return Response::erreur(405, 'METHODE_NON_AUTORISEE', 'Méthode HTTP non autorisée pour cette route.');
        }

        return Response::erreur(404, 'ROUTE_INCONNUE', 'Route inconnue.');
    }
}
