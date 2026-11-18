<?php
declare(strict_types=1);

namespace App\Services;

use App\Repositories\DemandeRepository;
use App\Support\ApiException;

/**
 * Règles métier des demandes de stage.
 *
 * Cycle de vie (table des transitions) :
 *   BROUILLON -> SOUMISE -> VALIDEE
 *                        -> REFUSEE
 * Une demande VALIDEE ou REFUSEE est terminale : toute autre transition
 * répond 409, jamais un succès silencieux.
 */
final class DemandeService
{
    /** @var array<string, list<string>> */
    private const TRANSITIONS = [
        'BROUILLON' => ['SOUMISE'],
        'SOUMISE' => ['VALIDEE', 'REFUSEE'],
        'VALIDEE' => [],
        'REFUSEE' => [],
    ];

    public function __construct(
        private readonly DemandeRepository $demandes = new DemandeRepository()
    ) {
    }

    /**
     * @return list<string>
     */
    public function transitionsDepuis(string $statut): array
    {
        return self::TRANSITIONS[$statut] ?? [];
    }

    public function transitionAutorisee(string $ancien, string $nouveau): bool
    {
        return in_array($nouveau, self::TRANSITIONS[$ancien] ?? [], true);
    }

    /**
     * @param array<string, mixed> $utilisateur
     * @return list<array<string, mixed>>
     */
    public function lister(array $utilisateur): array
    {
        return match ($utilisateur['role']) {
            'ETUDIANT' => $this->demandes->findByStudent(
                $this->exigerProfil($utilisateur, 'etudiant_id', 'Aucune fiche étudiant associée à ce compte.')
            ),
            'ENCADREUR' => $this->demandes->findByEncadreur(
                $this->exigerProfil($utilisateur, 'encadreur_id', 'Aucune fiche encadreur associée à ce compte.')
            ),
            'RESPONSABLE', 'ADMIN' => $this->demandes->findAll(),
            default => throw new ApiException(
                403,
                'ROLE_NON_AUTORISE',
                'Ce rôle ne peut pas consulter les demandes.'
            ),
        };
    }

    /**
     * @param array<string, mixed> $utilisateur
     * @return array<string, mixed>
     */
    public function detail(int $id, array $utilisateur): array
    {
        $demande = $this->demandes->findById($id);

        if ($demande === null) {
            throw new ApiException(404, 'DEMANDE_INCONNUE', 'Demande inconnue.');
        }

        $this->verifierAcces($demande, $utilisateur);

        return $demande;
    }

    /**
     * @param array<string, mixed> $corps
     * @param array<string, mixed> $utilisateur
     * @return array<string, mixed>
     */
    public function creer(array $corps, array $utilisateur): array
    {
        if ($utilisateur['role'] !== 'ETUDIANT') {
            throw new ApiException(
                403,
                'ROLE_NON_AUTORISE',
                'Seul un étudiant peut déposer une demande.'
            );
        }

        $etudiantId = $this->exigerProfil(
            $utilisateur,
            'etudiant_id',
            'Aucune fiche étudiant associée à ce compte.'
        );

        $donnees = $this->validerCreation($corps);
        $soumettre = $donnees['soumettre'];
        $dateDepot = $soumettre ? gmdate('Y-m-d H:i:s') : null;

        $id = $this->demandes->transaction(
            function () use ($donnees, $etudiantId, $soumettre, $dateDepot, $utilisateur): int {
                $id = $this->demandes->create([
                    'etudiant_id' => $etudiantId,
                    'entreprise_id' => $donnees['entreprise_id'],
                    'encadreur_id' => $donnees['encadreur_id'],
                    'intitule' => $donnees['intitule'],
                    'statut' => $soumettre ? 'SOUMISE' : 'BROUILLON',
                    'date_depot' => $dateDepot,
                    'date_debut' => $donnees['date_debut'],
                    'date_fin' => $donnees['date_fin'],
                ]);

                if ($soumettre) {
                    $this->demandes->ajouterHistorique(
                        $id,
                        null,
                        'SOUMISE',
                        (int) $utilisateur['id'],
                        null,
                        (string) $dateDepot
                    );
                }

                return $id;
            }
        );

        $demande = $this->demandes->findById($id);

        if ($demande === null) {
            throw new ApiException(500, 'ERREUR_INTERNE', 'Demande créée mais introuvable.');
        }

        return $demande;
    }

    /**
     * Décision du responsable : mise à jour du statut puis écriture de
     * l'historique dans la même transaction (rollback si l'une échoue).
     *
     * @param array<string, mixed> $corps
     * @param array<string, mixed> $utilisateur
     * @return array<string, mixed>
     */
    public function changerStatut(int $id, array $corps, array $utilisateur): array
    {
        if ($utilisateur['role'] !== 'RESPONSABLE') {
            throw new ApiException(
                403,
                'ROLE_NON_AUTORISE',
                'Seul le responsable pédagogique peut décider d’une demande.'
            );
        }

        $demande = $this->demandes->findById($id);

        if ($demande === null) {
            throw new ApiException(404, 'DEMANDE_INCONNUE', 'Demande inconnue.');
        }

        $statut = $corps['statut'] ?? null;

        if (!is_string($statut) || !in_array($statut, ['VALIDEE', 'REFUSEE'], true)) {
            throw new ApiException(
                422,
                'VALIDATION',
                'Statut de décision invalide.',
                ['statut' => 'Valeurs acceptées : VALIDEE, REFUSEE.']
            );
        }

        $motif = null;

        if ($statut === 'REFUSEE') {
            $motif = is_string($corps['motif'] ?? null) ? trim($corps['motif']) : '';
            $longueur = $this->longueur($motif);

            if ($longueur < 3 || $longueur > 255) {
                throw new ApiException(
                    422,
                    'VALIDATION',
                    'Un refus exige un motif de 3 à 255 caractères.',
                    ['motif' => 'Motif obligatoire et limité à 255 caractères.']
                );
            }
        }

        $ancienStatut = (string) $demande['statut'];

        if (!$this->transitionAutorisee($ancienStatut, $statut)) {
            throw new ApiException(
                409,
                'TRANSITION_INTERDITE',
                sprintf('Transition %s vers %s interdite.', $ancienStatut, $statut),
                [
                    'statut_actuel' => $ancienStatut,
                    'statut_demande' => $statut,
                    'transitions_possibles' => $this->transitionsDepuis($ancienStatut),
                ]
            );
        }

        $dateDecision = gmdate('Y-m-d H:i:s');

        $this->demandes->transaction(function () use (
            $id,
            $statut,
            $motif,
            $dateDecision,
            $ancienStatut,
            $utilisateur
        ): void {
            $this->demandes->updateStatus($id, $statut, $motif, $dateDecision);
            $this->demandes->ajouterHistorique(
                $id,
                $ancienStatut,
                $statut,
                (int) $utilisateur['id'],
                $motif,
                $dateDecision
            );
        });

        $demande = $this->demandes->findById($id);

        if ($demande === null) {
            throw new ApiException(500, 'ERREUR_INTERNE', 'Demande mise à jour mais introuvable.');
        }

        return $demande;
    }

    /**
     * @param array<string, mixed> $demande
     * @param array<string, mixed> $utilisateur
     */
    private function verifierAcces(array $demande, array $utilisateur): void
    {
        $role = $utilisateur['role'];

        if ($role === 'ETUDIANT'
            && (int) $demande['etudiant_utilisateur_id'] !== (int) $utilisateur['id']
        ) {
            throw new ApiException(
                403,
                'ACCES_REFUSE',
                'Cette demande appartient à un autre étudiant.'
            );
        }

        if ($role === 'ENCADREUR'
            && (int) $demande['encadreur_id'] !== (int) ($utilisateur['encadreur_id'] ?? 0)
        ) {
            throw new ApiException(
                403,
                'ACCES_REFUSE',
                'Cette demande n’est pas encadrée par ce compte.'
            );
        }

        if (!in_array($role, ['ETUDIANT', 'ENCADREUR', 'RESPONSABLE', 'ADMIN'], true)) {
            throw new ApiException(
                403,
                'ROLE_NON_AUTORISE',
                'Ce rôle ne peut pas consulter cette demande.'
            );
        }
    }

    /**
     * @param array<string, mixed> $corps
     * @return array{entreprise_id: int, encadreur_id: ?int, intitule: string, date_debut: string, date_fin: string, soumettre: bool}
     */
    private function validerCreation(array $corps): array
    {
        $details = [];

        $entrepriseId = $this->entierPositif($corps['entreprise_id'] ?? null);

        if ($entrepriseId === null) {
            $details['entreprise_id'] = 'Identifiant d’entreprise entier positif obligatoire.';
        } elseif (!$this->demandes->entrepriseExiste($entrepriseId)) {
            $details['entreprise_id'] = 'Entreprise inconnue.';
        }

        $encadreurId = null;

        if (array_key_exists('encadreur_id', $corps) && $corps['encadreur_id'] !== null) {
            $encadreurId = $this->entierPositif($corps['encadreur_id']);

            if ($encadreurId === null) {
                $details['encadreur_id'] = 'Identifiant d’encadreur entier positif, ou null.';
            } elseif (!$this->demandes->encadreurExiste($encadreurId)) {
                $details['encadreur_id'] = 'Encadreur inconnu.';
            }
        }

        $intitule = is_string($corps['intitule'] ?? null) ? trim($corps['intitule']) : '';
        $longueurIntitule = $this->longueur($intitule);

        if ($longueurIntitule < 5 || $longueurIntitule > 120) {
            $details['intitule'] = 'Intitulé de 5 à 120 caractères obligatoire.';
        }

        $dateDebut = is_string($corps['date_debut'] ?? null) ? $corps['date_debut'] : '';
        $dateFin = is_string($corps['date_fin'] ?? null) ? $corps['date_fin'] : '';

        if (!$this->dateValide($dateDebut)) {
            $details['date_debut'] = 'Date de début au format AAAA-MM-JJ.';
        }

        if (!$this->dateValide($dateFin)) {
            $details['date_fin'] = 'Date de fin au format AAAA-MM-JJ.';
        }

        if ($this->dateValide($dateDebut) && $this->dateValide($dateFin) && $dateFin <= $dateDebut) {
            $details['date_fin'] = 'La date de fin doit être postérieure à la date de début.';
        }

        $soumettre = $corps['soumettre'] ?? false;

        if (!is_bool($soumettre)) {
            $details['soumettre'] = 'Booléen attendu.';
        }

        if ($details !== []) {
            throw new ApiException(422, 'VALIDATION', 'Données invalides.', $details);
        }

        return [
            'entreprise_id' => (int) $entrepriseId,
            'encadreur_id' => $encadreurId,
            'intitule' => $intitule,
            'date_debut' => $dateDebut,
            'date_fin' => $dateFin,
            'soumettre' => (bool) $soumettre,
        ];
    }

    private function entierPositif(mixed $valeur): ?int
    {
        if (is_int($valeur)) {
            return $valeur > 0 ? $valeur : null;
        }

        if (is_string($valeur) && ctype_digit($valeur) && (int) $valeur > 0) {
            return (int) $valeur;
        }

        return null;
    }

    private function dateValide(string $valeur): bool
    {
        if (preg_match('/^(\d{4})-(\d{2})-(\d{2})$/', $valeur, $parties) !== 1) {
            return false;
        }

        return checkdate((int) $parties[2], (int) $parties[3], (int) $parties[1]);
    }

    private function longueur(string $valeur): int
    {
        return function_exists('mb_strlen') ? mb_strlen($valeur) : strlen($valeur);
    }

    /**
     * @param array<string, mixed> $utilisateur
     */
    private function exigerProfil(array $utilisateur, string $cle, string $message): int
    {
        $id = $utilisateur[$cle] ?? null;

        if (!is_int($id) || $id <= 0) {
            throw new ApiException(403, 'PROFIL_MANQUANT', $message);
        }

        return $id;
    }
}
