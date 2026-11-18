<?php
declare(strict_types=1);

namespace App\Support;

/**
 * Session PHP : un seul identifiant opaque côté navigateur, aucun rôle stocké
 * côté client. L'identifiant est régénéré à la connexion pour éviter la
 * fixation de session.
 */
final class Session
{
    private const NOM_COOKIE = 'SESSID_TP6';

    public static function demarrer(): void
    {
        if (session_status() === PHP_SESSION_ACTIVE) {
            return;
        }

        session_name(self::NOM_COOKIE);
        session_set_cookie_params([
            'lifetime' => 0,
            'path' => '/',
            'httponly' => true,
            'samesite' => 'Lax',
            // Passer à true derrière HTTPS ; false uniquement en local HTTP.
            'secure' => false,
        ]);

        // Identifiant inconnu refusé, cookie seul accepté : deux garde-fous
        // contre la fixation de session.
        ini_set('session.use_strict_mode', '1');
        ini_set('session.use_only_cookies', '1');

        // Certaines installations Debian réservent /var/lib/php/sessions à root.
        $dossier = session_save_path();
        if ($dossier === '' || !is_dir($dossier) || !is_writable($dossier)) {
            session_save_path(sys_get_temp_dir());
        }

        session_start();
    }

    public static function utilisateurId(): ?int
    {
        self::demarrer();

        $id = $_SESSION['utilisateur_id'] ?? null;

        if (is_int($id) && $id > 0) {
            return $id;
        }

        if (is_numeric($id) && (int) $id > 0) {
            return (int) $id;
        }

        return null;
    }

    public static function connecter(int $utilisateurId): void
    {
        self::demarrer();

        // Régénère l'identifiant AVANT d'écrire la session : l'ancien identifiant
        // éventuellement volé devient inutilisable.
        session_regenerate_id(true);

        $_SESSION = [
            'utilisateur_id' => $utilisateurId,
            'connecte_le' => time(),
        ];
    }

    public static function deconnecter(): void
    {
        self::demarrer();

        $_SESSION = [];
        session_regenerate_id(true);
    }
}
