<?php
declare(strict_types=1);

namespace App\Services;

use App\Repositories\UtilisateurRepository;
use App\Support\ApiException;
use App\Support\Session;

/**
 * Authentification par session.
 * Le mot de passe n'est jamais stocké en clair : seule l'empreinte bcrypt est
 * comparée avec password_verify().
 */
final class AuthService
{
    /**
     * Empreinte factice utilisée quand l'e-mail est inconnu : password_verify()
     * travaille quand même, ce qui limite l'écart de temps entre « compte
     * inexistant » et « mot de passe faux ».
     */
    private const EMPREINTE_FACTICE =
        '$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm';

    public function __construct(
        private readonly UtilisateurRepository $utilisateurs = new UtilisateurRepository()
    ) {
    }

    /**
     * @param array<string, mixed> $corps
     * @return array<string, mixed> utilisateur public (sans l'empreinte)
     */
    public function connecter(array $corps): array
    {
        $email = $corps['email'] ?? null;
        $motDePasse = $corps['mot_de_passe'] ?? null;

        $details = [];

        if (!is_string($email) || filter_var($email, FILTER_VALIDATE_EMAIL) === false) {
            $details['email'] = 'Adresse e-mail invalide.';
        }

        if (!is_string($motDePasse) || $motDePasse === '') {
            $details['mot_de_passe'] = 'Mot de passe obligatoire.';
        }

        if ($details !== []) {
            throw new ApiException(422, 'VALIDATION', 'Identifiants incomplets.', $details);
        }

        // Les deux valeurs sont des chaînes : la validation ci-dessus l'a garanti.
        $utilisateur = $this->utilisateurs->trouverParEmail($email);
        $empreinte = is_array($utilisateur)
            ? (string) $utilisateur['mot_de_passe_hash']
            : self::EMPREINTE_FACTICE;

        $motDePasseValide = password_verify($motDePasse, $empreinte);

        if ($utilisateur === null || !$motDePasseValide) {
            throw new ApiException(
                401,
                'IDENTIFIANTS_INVALIDES',
                'E-mail ou mot de passe incorrect.'
            );
        }

        if (!(bool) $utilisateur['actif']) {
            throw new ApiException(403, 'COMPTE_INACTIF', 'Ce compte est désactivé.');
        }

        Session::connecter((int) $utilisateur['id']);

        return self::presenter($utilisateur);
    }

    /**
     * @return array<string, mixed>|null
     */
    public function courant(): ?array
    {
        $id = Session::utilisateurId();

        if ($id === null) {
            return null;
        }

        $utilisateur = $this->utilisateurs->trouverParId($id);

        if ($utilisateur === null || !(bool) $utilisateur['actif']) {
            Session::deconnecter();

            return null;
        }

        return self::presenter($utilisateur);
    }

    /**
     * @return array<string, mixed>
     */
    public function exigerUtilisateur(): array
    {
        $utilisateur = $this->courant();

        if ($utilisateur === null) {
            throw new ApiException(401, 'NON_AUTHENTIFIE', 'Authentification requise.');
        }

        return $utilisateur;
    }

    /**
     * @param list<string> $roles
     * @return array<string, mixed>
     */
    public function exigerRole(array $roles): array
    {
        $utilisateur = $this->exigerUtilisateur();

        if (!in_array($utilisateur['role'], $roles, true)) {
            throw new ApiException(
                403,
                'ROLE_NON_AUTORISE',
                'Ce rôle n’est pas autorisé pour cette action.',
                ['role' => $utilisateur['role']]
            );
        }

        return $utilisateur;
    }

    public function deconnecter(): void
    {
        Session::deconnecter();
    }

    /**
     * @param array<string, mixed> $utilisateur
     * @return array<string, mixed>
     */
    private static function presenter(array $utilisateur): array
    {
        return [
            'id' => (int) $utilisateur['id'],
            'email' => (string) $utilisateur['email'],
            'role' => (string) $utilisateur['role'],
            'nom' => (string) $utilisateur['nom'],
            'prenom' => (string) $utilisateur['prenom'],
            'etudiant_id' => $utilisateur['etudiant_id'] !== null
                ? (int) $utilisateur['etudiant_id']
                : null,
            'encadreur_id' => $utilisateur['encadreur_id'] !== null
                ? (int) $utilisateur['encadreur_id']
                : null,
        ];
    }
}
