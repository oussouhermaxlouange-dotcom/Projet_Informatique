-- Projet informatique 2 — L3 SIL
-- Plateforme de suivi des conventions de stage et des soutenances
-- 001_schema.sql — création du schéma sur une base vide
-- Dialecte : MySQL 8 / MariaDB 11
-- Exécution : mysql -u root < 001_schema.sql

SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS tp3_conventions
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE tp3_conventions;

SET FOREIGN_KEY_CHECKS = 0;
DROP VIEW IF EXISTS v_delai_publication;
DROP VIEW IF EXISTS v_planning_soutenance;
DROP VIEW IF EXISTS v_soutenances_conflits;
DROP VIEW IF EXISTS v_conventions_sans_encadreur;
DROP TABLE IF EXISTS historique;
DROP TABLE IF EXISTS soutenance;
DROP TABLE IF EXISTS disponibilite;
DROP TABLE IF EXISTS convention;
DROP TABLE IF EXISTS salle;
DROP TABLE IF EXISTS entreprise;
DROP TABLE IF EXISTS encadreur;
DROP TABLE IF EXISTS etudiant;
DROP TABLE IF EXISTS utilisateur;
SET FOREIGN_KEY_CHECKS = 1;

-- Comptes et rôles : une seule table d'identité, le rôle porte les droits.
CREATE TABLE utilisateur (
  id                INT UNSIGNED NOT NULL AUTO_INCREMENT,
  email             VARCHAR(100) NOT NULL,
  mot_de_passe_hash VARCHAR(255) NOT NULL,
  role              ENUM('ETUDIANT','ENCADREUR','RESPONSABLE','ADMIN','DEVELOPPEUR') NOT NULL,
  nom               VARCHAR(60)  NOT NULL,
  prenom            VARCHAR(60)  NOT NULL,
  actif             TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  UNIQUE KEY uk_utilisateur_email (email),
  CONSTRAINT ck_utilisateur_email CHECK (email LIKE '%_@_%._%')
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Étudiant : un compte, une seule fiche (1—0..1).
CREATE TABLE etudiant (
  id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
  utilisateur_id  INT UNSIGNED NOT NULL,
  numero_etudiant VARCHAR(20)  NOT NULL,
  filiere         VARCHAR(60)  NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_etudiant_utilisateur (utilisateur_id),
  UNIQUE KEY uk_etudiant_numero (numero_etudiant),
  CONSTRAINT fk_etudiant_utilisateur FOREIGN KEY (utilisateur_id)
    REFERENCES utilisateur (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Encadreur : un compte, une seule fiche (1—0..1).
CREATE TABLE encadreur (
  id             INT UNSIGNED NOT NULL AUTO_INCREMENT,
  utilisateur_id INT UNSIGNED NOT NULL,
  grade          VARCHAR(60)  NOT NULL,
  specialite     VARCHAR(80)  NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_encadreur_utilisateur (utilisateur_id),
  CONSTRAINT fk_encadreur_utilisateur FOREIGN KEY (utilisateur_id)
    REFERENCES utilisateur (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE entreprise (
  id      INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nom     VARCHAR(80)  NOT NULL,
  ville   VARCHAR(60)  NOT NULL,
  contact VARCHAR(100) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_entreprise_nom_ville (nom, ville)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Référentiel des salles : un nom unique, une capacité positive.
CREATE TABLE salle (
  id       INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nom      VARCHAR(30)  NOT NULL,
  capacite SMALLINT UNSIGNED NOT NULL,
  batiment VARCHAR(40)  NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_salle_nom (nom),
  CONSTRAINT ck_salle_capacite CHECK (capacite BETWEEN 1 AND 500)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Convention de stage : une entreprise, un étudiant, au plus un encadreur.
-- Cycle : BROUILLON -> SOUMISE -> VALIDEE | REFUSEE
-- Une convention validée peut rester sans encadreur : la vue
-- v_conventions_sans_encadreur sert d'indicateur d'affectation.
CREATE TABLE convention (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  etudiant_id   INT UNSIGNED NOT NULL,
  entreprise_id INT UNSIGNED NOT NULL,
  encadreur_id  INT UNSIGNED NULL,
  intitule      VARCHAR(120) NOT NULL,
  statut        ENUM('BROUILLON','SOUMISE','VALIDEE','REFUSEE') NOT NULL DEFAULT 'BROUILLON',
  motif_refus   VARCHAR(255) NULL,
  date_depot    DATETIME NULL,
  date_decision DATETIME NULL,
  date_debut    DATE NOT NULL,
  date_fin      DATE NOT NULL,
  PRIMARY KEY (id),
  -- Index exigé par la clé étrangère composite de soutenance.
  UNIQUE KEY uk_convention_id_encadreur (id, encadreur_id),
  KEY idx_convention_etudiant (etudiant_id),
  KEY idx_convention_entreprise (entreprise_id),
  KEY idx_convention_encadreur (encadreur_id),
  KEY idx_convention_statut (statut),
  CONSTRAINT fk_convention_etudiant FOREIGN KEY (etudiant_id)
    REFERENCES etudiant (id) ON DELETE CASCADE,
  CONSTRAINT fk_convention_entreprise FOREIGN KEY (entreprise_id)
    REFERENCES entreprise (id),
  CONSTRAINT fk_convention_encadreur FOREIGN KEY (encadreur_id)
    REFERENCES encadreur (id) ON DELETE SET NULL,
  CONSTRAINT ck_convention_motif CHECK (statut <> 'REFUSEE' OR motif_refus IS NOT NULL),
  CONSTRAINT ck_convention_depot CHECK (statut = 'BROUILLON' OR date_depot IS NOT NULL),
  CONSTRAINT ck_convention_decision
    CHECK (statut NOT IN ('VALIDEE','REFUSEE') OR date_decision IS NOT NULL),
  CONSTRAINT ck_convention_periode CHECK (date_fin > date_debut)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Créneaux déclarés par un encadreur pour les soutenances.
CREATE TABLE disponibilite (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  encadreur_id  INT UNSIGNED NOT NULL,
  date_debut    DATETIME NOT NULL,
  date_fin      DATETIME NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_disponibilite_creneau (encadreur_id, date_debut),
  KEY idx_disponibilite_encadreur (encadreur_id),
  CONSTRAINT fk_disponibilite_encadreur FOREIGN KEY (encadreur_id)
    REFERENCES encadreur (id) ON DELETE CASCADE,
  CONSTRAINT ck_disponibilite_ordre CHECK (date_fin > date_debut)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Soutenance : une convention donne au plus une soutenance.
-- L'encadreur de la soutenance est nécessairement celui de la convention
-- (clé étrangère composite). Les doublons exacts salle/créneau et
-- encadreur/créneau sont interdits par les clés UNIQUE ; les chevauchements
-- réels sont contrôlés par la vue v_soutenances_conflits.
CREATE TABLE soutenance (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  convention_id INT UNSIGNED NOT NULL,
  encadreur_id  INT UNSIGNED NOT NULL,
  salle_id      INT UNSIGNED NOT NULL,
  date_heure    DATETIME NOT NULL,
  duree_min     SMALLINT UNSIGNED NOT NULL DEFAULT 45,
  statut        ENUM('PLANIFIEE','REALISEE','ANNULEE') NOT NULL DEFAULT 'PLANIFIEE',
  date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_soutenance_convention (convention_id),
  UNIQUE KEY uk_soutenance_salle_creneau (salle_id, date_heure),
  UNIQUE KEY uk_soutenance_encadreur_creneau (encadreur_id, date_heure),
  KEY idx_soutenance_convention_encadreur (convention_id, encadreur_id),
  KEY idx_soutenance_salle (salle_id),
  CONSTRAINT fk_soutenance_convention_encadreur
    FOREIGN KEY (convention_id, encadreur_id)
    REFERENCES convention (id, encadreur_id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_soutenance_salle FOREIGN KEY (salle_id)
    REFERENCES salle (id),
  CONSTRAINT ck_soutenance_duree CHECK (duree_min BETWEEN 20 AND 240)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Journal des décisions : une ligne par changement de statut.
CREATE TABLE historique (
  id             INT UNSIGNED NOT NULL AUTO_INCREMENT,
  convention_id  INT UNSIGNED NOT NULL,
  ancien_statut  ENUM('BROUILLON','SOUMISE','VALIDEE','REFUSEE') NULL,
  nouveau_statut ENUM('BROUILLON','SOUMISE','VALIDEE','REFUSEE') NOT NULL,
  auteur_id      INT UNSIGNED NOT NULL,
  motif          VARCHAR(255) NULL,
  date_evenement DATETIME NOT NULL,
  PRIMARY KEY (id),
  KEY idx_historique_convention_date (convention_id, date_evenement),
  KEY idx_historique_auteur (auteur_id),
  CONSTRAINT fk_historique_convention FOREIGN KEY (convention_id)
    REFERENCES convention (id) ON DELETE CASCADE,
  CONSTRAINT fk_historique_auteur FOREIGN KEY (auteur_id)
    REFERENCES utilisateur (id),
  CONSTRAINT ck_historique_motif
    CHECK (nouveau_statut <> 'REFUSEE' OR motif IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indicateur n° 2 du cadrage : conventions validées restées sans encadreur.
CREATE OR REPLACE VIEW v_conventions_sans_encadreur AS
SELECT c.id            AS convention_id,
       u.nom           AS etudiant_nom,
       u.prenom        AS etudiant_prenom,
       e.numero_etudiant,
       c.date_decision
FROM convention c
JOIN etudiant e    ON e.id = c.etudiant_id
JOIN utilisateur u ON u.id = e.utilisateur_id
WHERE c.statut = 'VALIDEE'
  AND c.encadreur_id IS NULL;

-- Indicateur n° 3 du cadrage : chevauchements de salle ou d'encadreur.
CREATE OR REPLACE VIEW v_soutenances_conflits AS
SELECT a.id AS soutenance_1,
       b.id AS soutenance_2,
       CASE
         WHEN a.salle_id = b.salle_id AND a.encadreur_id = b.encadreur_id THEN 'SALLE+ENCADREUR'
         WHEN a.salle_id = b.salle_id THEN 'SALLE'
         ELSE 'ENCADREUR'
       END AS type_conflit,
       a.salle_id,
       a.encadreur_id,
       a.date_heure AS debut_1,
       b.date_heure AS debut_2
FROM soutenance a
JOIN soutenance b
  ON a.id < b.id
 AND a.statut <> 'ANNULEE'
 AND b.statut <> 'ANNULEE'
 AND (a.salle_id = b.salle_id OR a.encadreur_id = b.encadreur_id)
 AND a.date_heure < b.date_heure + INTERVAL b.duree_min MINUTE
 AND b.date_heure < a.date_heure + INTERVAL a.duree_min MINUTE;

-- Planning lisible par le secrétariat et par les étudiants.
CREATE OR REPLACE VIEW v_planning_soutenance AS
SELECT s.id AS soutenance_id,
       s.date_heure,
       s.duree_min,
       s.statut AS statut_soutenance,
       sa.nom AS salle,
       sa.batiment,
       c.id AS convention_id,
       c.intitule,
       e.numero_etudiant,
       CONCAT(u.prenom, ' ', u.nom) AS etudiant,
       ent.nom AS entreprise,
       CONCAT(ue.prenom, ' ', ue.nom) AS encadreur
FROM soutenance s
JOIN convention c   ON c.id = s.convention_id
JOIN etudiant e     ON e.id = c.etudiant_id
JOIN utilisateur u  ON u.id = e.utilisateur_id
JOIN entreprise ent ON ent.id = c.entreprise_id
JOIN salle sa       ON sa.id = s.salle_id
JOIN encadreur enc  ON enc.id = s.encadreur_id
JOIN utilisateur ue ON ue.id = enc.utilisateur_id;

-- Indicateur n° 1 du cadrage : délai entre décision et publication du planning.
CREATE OR REPLACE VIEW v_delai_publication AS
SELECT c.id AS convention_id,
       c.date_decision,
       s.date_creation AS date_publication,
       s.date_heure AS date_soutenance,
       DATEDIFF(s.date_creation, c.date_decision) AS delai_jours,
       CASE WHEN DATEDIFF(s.date_creation, c.date_decision) <= 5
            THEN 'OUI' ELSE 'NON' END AS cible_5j
FROM convention c
JOIN soutenance s ON s.convention_id = c.id
WHERE c.statut = 'VALIDEE';
