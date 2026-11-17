-- Projet informatique 2 — L3 SIL
-- Plateforme de suivi des conventions de stage et des soutenances
-- 004_tests_contraintes.sql — insertions volontairement invalides
-- Exécution : mysql --force -u root < 004_tests_contraintes.sql
-- Chaque erreur est attendue ; aucune ligne ne doit rester en base.

SET NAMES utf8mb4;
USE tp3_conventions;

-- 1. Refus sans motif : ck_convention_motif
INSERT INTO convention (etudiant_id, entreprise_id, intitule, statut,
                        motif_refus, date_depot, date_decision, date_debut, date_fin)
VALUES (1, 1, 'Refus sans motif', 'REFUSEE', NULL,
        '2026-11-01 09:00:00', '2026-11-02 09:00:00', '2027-02-01', '2027-05-31');

-- 2. Email sans arobase : ck_utilisateur_email
INSERT INTO utilisateur (email, mot_de_passe_hash, role, nom, prenom)
VALUES ('sans-arobase.test', 'x', 'ETUDIANT', 'TEST', 'Invalide');

-- 3. Entreprise inexistante : fk_convention_entreprise
INSERT INTO convention (etudiant_id, entreprise_id, intitule, statut,
                        date_debut, date_fin)
VALUES (2, 999, 'Entreprise inexistante', 'BROUILLON', '2027-02-01', '2027-05-31');

-- 4. Période inversée : ck_convention_periode
INSERT INTO convention (etudiant_id, entreprise_id, intitule, statut,
                        date_debut, date_fin)
VALUES (2, 2, 'Période inversée', 'BROUILLON', '2027-06-30', '2027-01-01');

-- 5 et 6. Conflits de planning : doublon exact puis chevauchement.
START TRANSACTION;
UPDATE convention SET encadreur_id = 1 WHERE id = 6;

-- 5. Même salle et même créneau : uk_soutenance_salle_creneau
INSERT INTO soutenance (convention_id, encadreur_id, salle_id, date_heure,
                        duree_min, date_creation)
VALUES (6, 1, 1, '2027-06-15 09:00:00', 45, '2026-11-02 10:00:00');

-- 6. Créneau décalé de 30 min, même salle : accepté par les UNIQUE,
--    mais détecté par v_soutenances_conflits.
INSERT INTO soutenance (convention_id, encadreur_id, salle_id, date_heure,
                        duree_min, date_creation)
VALUES (6, 1, 1, '2027-06-15 09:30:00', 45, '2026-11-02 10:00:00');

SELECT COUNT(*) AS conflits_pendant_transaction FROM v_soutenances_conflits;
ROLLBACK;

SELECT COUNT(*) AS conflits_apres_rollback FROM v_soutenances_conflits;
SELECT COUNT(*) AS conventions_apres_tests FROM convention;
SELECT COUNT(*) AS utilisateurs_apres_tests FROM utilisateur;
