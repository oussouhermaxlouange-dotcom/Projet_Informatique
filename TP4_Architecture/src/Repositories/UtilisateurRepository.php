<?php
declare(strict_types=1);

namespace App\Repositories;

use PDO;

/**
 * Accès à la table utilisateur.
 * Les comptes portent le rôle ; les fiches étudiant/encadreur sont jointes
 * pour éviter une seconde requête au moment de l'authentification.
 */
final class UtilisateurRepository
{
    private const SELECTION = <<<'SQL'
        SELECT u.id,
               u.email,
               u.mot_de_passe_hash,
               u.role,
               u.nom,
               u.prenom,
               u.actif,
               e.id  AS etudiant_id,
               enc.id AS encadreur_id
        FROM utilisateur u
        LEFT JOIN etudiant e   ON e.utilisateur_id = u.id
        LEFT JOIN encadreur enc ON enc.utilisateur_id = u.id
        SQL;

    /**
     * @return array<string, mixed>|null
     */
    public function trouverParEmail(string $email): ?array
    {
        $requete = Database::connexion()->prepare(
            self::SELECTION . ' WHERE u.email = :email LIMIT 1'
        );
        $requete->execute(['email' => $email]);

        $ligne = $requete->fetch(PDO::FETCH_ASSOC);

        return $ligne === false ? null : $ligne;
    }

    /**
     * @return array<string, mixed>|null
     */
    public function trouverParId(int $id): ?array
    {
        $requete = Database::connexion()->prepare(
            self::SELECTION . ' WHERE u.id = :id LIMIT 1'
        );
        $requete->execute(['id' => $id]);

        $ligne = $requete->fetch(PDO::FETCH_ASSOC);

        return $ligne === false ? null : $ligne;
    }
}
