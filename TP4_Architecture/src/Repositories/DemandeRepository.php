<?php
declare(strict_types=1);

namespace App\Repositories;

use PDO;
use Throwable;

/**
 * Accès aux demandes de stage.
 *
 * Une demande de stage est stockée dans la table `convention` du modèle TP3 :
 * même cycle de vie (BROUILLON, SOUMISE, VALIDEE, REFUSEE) et même journal
 * (`historique`). Aucun SQL ne sort de cette classe.
 */
final class DemandeRepository
{
    private const SELECTION = <<<'SQL'
        SELECT c.id,
               c.etudiant_id,
               c.entreprise_id,
               c.encadreur_id,
               c.intitule,
               c.statut,
               c.motif_refus,
               c.date_depot,
               c.date_decision,
               c.date_debut,
               c.date_fin,
               e.utilisateur_id AS etudiant_utilisateur_id,
               CONCAT(u.prenom, ' ', u.nom) AS etudiant,
               ent.nom AS entreprise
        FROM convention c
        JOIN etudiant e     ON e.id = c.etudiant_id
        JOIN utilisateur u  ON u.id = e.utilisateur_id
        JOIN entreprise ent ON ent.id = c.entreprise_id
        SQL;

    /**
     * @return array<string, mixed>|null
     */
    public function findById(int $id): ?array
    {
        $requete = Database::connexion()->prepare(
            self::SELECTION . ' WHERE c.id = :id LIMIT 1'
        );
        $requete->execute(['id' => $id]);

        $ligne = $requete->fetch(PDO::FETCH_ASSOC);

        return $ligne === false ? null : $ligne;
    }

    /**
     * @return list<array<string, mixed>>
     */
    public function findByStudent(int $etudiantId): array
    {
        $requete = Database::connexion()->prepare(
            self::SELECTION
            . ' WHERE c.etudiant_id = :etudiant_id'
            . ' ORDER BY c.date_depot DESC, c.id DESC'
        );
        $requete->execute(['etudiant_id' => $etudiantId]);

        return $requete->fetchAll(PDO::FETCH_ASSOC);
    }

    /**
     * Demandes encadrées par un enseignant.
     *
     * @return list<array<string, mixed>>
     */
    public function findByEncadreur(int $encadreurId): array
    {
        $requete = Database::connexion()->prepare(
            self::SELECTION
            . ' WHERE c.encadreur_id = :encadreur_id'
            . ' ORDER BY c.date_depot DESC, c.id DESC'
        );
        $requete->execute(['encadreur_id' => $encadreurId]);

        return $requete->fetchAll(PDO::FETCH_ASSOC);
    }

    /**
     * Liste destinée au responsable pédagogique.
     *
     * @return list<array<string, mixed>>
     */
    public function findAll(): array
    {
        $requete = Database::connexion()->query(
            self::SELECTION . ' ORDER BY c.date_depot DESC, c.id DESC'
        );

        return $requete->fetchAll(PDO::FETCH_ASSOC);
    }

    /**
     * @param array{etudiant_id: int, entreprise_id: int, encadreur_id: ?int, intitule: string, statut: string, date_depot: ?string, date_debut: string, date_fin: string} $donnees
     */
    public function create(array $donnees): int
    {
        $requete = Database::connexion()->prepare(
            <<<'SQL'
            INSERT INTO convention
                (etudiant_id, entreprise_id, encadreur_id, intitule, statut,
                 motif_refus, date_depot, date_decision, date_debut, date_fin)
            VALUES
                (:etudiant_id, :entreprise_id, :encadreur_id, :intitule, :statut,
                 NULL, :date_depot, NULL, :date_debut, :date_fin)
            SQL
        );

        $requete->execute([
            'etudiant_id' => $donnees['etudiant_id'],
            'entreprise_id' => $donnees['entreprise_id'],
            'encadreur_id' => $donnees['encadreur_id'],
            'intitule' => $donnees['intitule'],
            'statut' => $donnees['statut'],
            'date_depot' => $donnees['date_depot'],
            'date_debut' => $donnees['date_debut'],
            'date_fin' => $donnees['date_fin'],
        ]);

        return (int) Database::connexion()->lastInsertId();
    }

    /**
     * Met à jour le statut d'une demande. Le motif reste NULL pour une validation,
     * conformément à la contrainte ck_convention_motif du schéma.
     */
    public function updateStatus(int $id, string $statut, ?string $motif, ?string $dateDecision): bool
    {
        $requete = Database::connexion()->prepare(
            <<<'SQL'
            UPDATE convention
               SET statut = :statut,
                   motif_refus = :motif,
                   date_decision = :date_decision
             WHERE id = :id
            SQL
        );

        $requete->execute([
            'statut' => $statut,
            'motif' => $motif,
            'date_decision' => $dateDecision,
            'id' => $id,
        ]);

        return $requete->rowCount() === 1;
    }

    public function ajouterHistorique(
        int $demandeId,
        ?string $ancienStatut,
        string $nouveauStatut,
        int $auteurId,
        ?string $motif,
        string $dateEvenement
    ): void {
        $requete = Database::connexion()->prepare(
            <<<'SQL'
            INSERT INTO historique
                (convention_id, ancien_statut, nouveau_statut, auteur_id, motif, date_evenement)
            VALUES
                (:convention_id, :ancien_statut, :nouveau_statut, :auteur_id, :motif, :date_evenement)
            SQL
        );

        $requete->execute([
            'convention_id' => $demandeId,
            'ancien_statut' => $ancienStatut,
            'nouveau_statut' => $nouveauStatut,
            'auteur_id' => $auteurId,
            'motif' => $motif,
            'date_evenement' => $dateEvenement,
        ]);
    }

    public function entrepriseExiste(int $id): bool
    {
        $requete = Database::connexion()->prepare('SELECT 1 FROM entreprise WHERE id = :id');
        $requete->execute(['id' => $id]);

        return $requete->fetchColumn() !== false;
    }

    public function encadreurExiste(int $id): bool
    {
        $requete = Database::connexion()->prepare('SELECT 1 FROM encadreur WHERE id = :id');
        $requete->execute(['id' => $id]);

        return $requete->fetchColumn() !== false;
    }

    /**
     * Exécute une opération dans une transaction : commit si tout passe,
     * rollback complet à la moindre exception.
     */
    public function transaction(callable $operation): mixed
    {
        $pdo = Database::connexion();
        $pdo->beginTransaction();

        try {
            $resultat = $operation();
            $pdo->commit();

            return $resultat;
        } catch (Throwable $exception) {
            if ($pdo->inTransaction()) {
                $pdo->rollBack();
            }

            throw $exception;
        }
    }
}
