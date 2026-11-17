-- Projet informatique 2 — L3 SIL
-- Plateforme de suivi des conventions de stage et des soutenances
-- 002_seed.sql — jeu d'essai fictif (aucune donnée réelle)
-- Attendu : 8 comptes, 3 étudiants, 2 encadreurs, 2 entreprises, 3 salles,
--           6 conventions, 4 disponibilités, 2 soutenances, 9 historiques.
-- Mot de passe commun des comptes de démonstration : Demo1234!
-- Empreinte produite par password_hash('Demo1234!', PASSWORD_DEFAULT) sous PHP 8.

SET NAMES utf8mb4;
USE tp3_conventions;

INSERT INTO utilisateur (id, email, mot_de_passe_hash, role, nom, prenom, actif) VALUES
  (1, 'sena.houngbo@univ.test',      '$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm', 'ETUDIANT',    'HOUNGBO', 'Sènami', 1),
  (2, 'ibrahim.sanni@univ.test',     '$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm', 'ETUDIANT',    'SANNI',   'Ibrahim',1),
  (3, 'grace.amegan@univ.test',      '$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm', 'ETUDIANT',    'AMEGAN',  'Grâce',  1),
  (4, 'sylvain.kiki@univ.test',      '$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm', 'ENCADREUR',   'KIKI',    'Sylvain',1),
  (5, 'mireille.zinsou@univ.test',   '$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm', 'ENCADREUR',   'ZINSOU',  'Mireille',1),
  (6, 'responsable.pedago@univ.test','$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm', 'RESPONSABLE', 'ADJAHO',  'Pascal', 1),
  (7, 'admin.siege@univ.test',       '$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm', 'ADMIN',       'da SILVA','Ruth',   1),
  (8, 'dev.equipe@univ.test',        '$2y$10$w8vj0PJ5HJkVug46z0gCgeQbKFAUvmEMRLbgCLqNUQ5VDvoiPCIXm', 'DEVELOPPEUR', 'TOSSA',   'Éric',   1);

INSERT INTO etudiant (id, utilisateur_id, numero_etudiant, filiere) VALUES
  (1, 1, 'ETU-2026-014', 'SIL'),
  (2, 2, 'ETU-2026-027', 'SIL'),
  (3, 3, 'ETU-2026-039', 'SIL');

INSERT INTO encadreur (id, utilisateur_id, grade, specialite) VALUES
  (1, 4, 'Maître de conférences', 'Bases de données'),
  (2, 5, 'Assistant',             'Génie logiciel');

INSERT INTO entreprise (id, nom, ville, contact) VALUES
  (1, 'Studio Kora',            'Porto-Novo', 'contact@studio-kora.test'),
  (2, 'Données et Territoires', 'Cotonou',    'rh@donnees-territoires.test');

INSERT INTO salle (id, nom, capacite, batiment) VALUES
  (1, 'A-101',   40, 'Bâtiment A'),
  (2, 'B-204',   30, 'Bâtiment B'),
  (3, 'Amphi C', 120, 'Bâtiment C');

-- Une convention par étape du cycle, plus une validée sans encadreur
-- (indicateur d'affectation) et une seconde validée prête à soutenir.
INSERT INTO convention (id, etudiant_id, entreprise_id, encadreur_id, intitule,
                        statut, motif_refus, date_depot, date_decision,
                        date_debut, date_fin) VALUES
  (1, 1, 1, NULL, 'Application de suivi des tournées de collecte',
      'BROUILLON', NULL, NULL, NULL, '2027-02-01', '2027-05-31'),
  (2, 2, 2, NULL, 'Tableau de bord des indicateurs territoriaux',
      'SOUMISE', NULL, '2026-11-10 09:30:00', NULL, '2027-03-01', '2027-06-30'),
  (3, 3, 1, 1, 'Refonte du portail documentaire',
      'VALIDEE', NULL, '2026-10-15 10:00:00', '2026-10-22 16:00:00',
      '2027-01-11', '2027-04-30'),
  (4, 1, 2, 2, 'Automatisation des rapports de collecte',
      'VALIDEE', NULL, '2026-10-18 14:00:00', '2026-10-25 11:30:00',
      '2027-02-08', '2027-05-28'),
  (5, 2, 1, NULL, 'Maintenance du réseau de capteurs',
      'REFUSEE', 'Période de stage incompatible avec le calendrier de la filière',
      '2026-10-08 08:45:00', '2026-10-12 15:10:00', '2027-01-04', '2027-03-29'),
  (6, 3, 2, NULL, 'Entrepôt de données des conventions',
      'VALIDEE', NULL, '2026-10-20 11:00:00', '2026-10-28 09:00:00',
      '2027-02-15', '2027-06-15');

INSERT INTO disponibilite (id, encadreur_id, date_debut, date_fin) VALUES
  (1, 1, '2027-06-15 08:00:00', '2027-06-15 12:00:00'),
  (2, 1, '2027-06-16 08:00:00', '2027-06-16 12:00:00'),
  (3, 2, '2027-06-15 08:00:00', '2027-06-15 12:00:00'),
  (4, 2, '2027-06-17 14:00:00', '2027-06-17 18:00:00');

-- Deux soutenances publiées dans les cinq jours suivant la décision.
INSERT INTO soutenance (id, convention_id, encadreur_id, salle_id, date_heure,
                        duree_min, statut, date_creation) VALUES
  (1, 3, 1, 1, '2027-06-15 09:00:00', 45, 'PLANIFIEE', '2026-10-26 10:00:00'),
  (2, 4, 2, 2, '2027-06-15 11:00:00', 45, 'PLANIFIEE', '2026-10-30 09:30:00');

INSERT INTO historique (convention_id, ancien_statut, nouveau_statut, auteur_id, motif, date_evenement) VALUES
  (2, NULL,      'SOUMISE',  2, NULL, '2026-11-10 09:30:00'),
  (3, NULL,      'SOUMISE',  3, NULL, '2026-10-15 10:00:00'),
  (3, 'SOUMISE', 'VALIDEE',  6, NULL, '2026-10-22 16:00:00'),
  (4, NULL,      'SOUMISE',  1, NULL, '2026-10-18 14:00:00'),
  (4, 'SOUMISE', 'VALIDEE',  6, NULL, '2026-10-25 11:30:00'),
  (5, NULL,      'SOUMISE',  2, NULL, '2026-10-08 08:45:00'),
  (5, 'SOUMISE', 'REFUSEE',  6, 'Période de stage incompatible avec le calendrier de la filière', '2026-10-12 15:10:00'),
  (6, NULL,      'SOUMISE',  3, NULL, '2026-10-20 11:00:00'),
  (6, 'SOUMISE', 'VALIDEE',  6, NULL, '2026-10-28 09:00:00');
