-- Projet informatique 2 — L3 SIL
-- Plateforme de suivi des conventions de stage et des soutenances
-- 003_verification.sql — contrôles après chargement du jeu d'essai
-- Exécution : mysql -u root < 003_verification.sql

SET NAMES utf8mb4;
USE tp3_conventions;

SELECT 'utilisateur'  AS table_, COUNT(*) AS lignes FROM utilisateur
UNION ALL SELECT 'etudiant',      COUNT(*) FROM etudiant
UNION ALL SELECT 'encadreur',     COUNT(*) FROM encadreur
UNION ALL SELECT 'entreprise',    COUNT(*) FROM entreprise
UNION ALL SELECT 'salle',         COUNT(*) FROM salle
UNION ALL SELECT 'convention',    COUNT(*) FROM convention
UNION ALL SELECT 'disponibilite', COUNT(*) FROM disponibilite
UNION ALL SELECT 'soutenance',    COUNT(*) FROM soutenance
UNION ALL SELECT 'historique',    COUNT(*) FROM historique;

SELECT statut, COUNT(*) AS conventions
FROM convention
GROUP BY statut
ORDER BY FIELD(statut, 'BROUILLON', 'SOUMISE', 'VALIDEE', 'REFUSEE');

SELECT COUNT(*) AS conventions_validees_sans_encadreur
FROM v_conventions_sans_encadreur;

SELECT c.id AS convention_id,
       CONCAT(u.prenom, ' ', u.nom) AS etudiant,
       c.statut,
       CONCAT(COALESCE(enc.prenom, '—'), ' ', COALESCE(enc.nom, '')) AS encadreur,
       c.date_decision
FROM convention c
JOIN etudiant e      ON e.id = c.etudiant_id
JOIN utilisateur u   ON u.id = e.utilisateur_id
LEFT JOIN encadreur en ON en.id = c.encadreur_id
LEFT JOIN utilisateur enc ON enc.id = en.utilisateur_id
ORDER BY c.id;

SELECT s.id AS id,
       DATE_FORMAT(s.date_heure, '%d/%m/%Y %H:%i') AS creneau,
       s.duree_min AS duree,
       p.salle,
       p.etudiant,
       p.entreprise,
       p.encadreur
FROM soutenance s
JOIN v_planning_soutenance p ON p.soutenance_id = s.id
ORDER BY s.date_heure;

SELECT convention_id, date_decision, date_publication,
       delai_jours, cible_5j
FROM v_delai_publication
ORDER BY convention_id;

SELECT COUNT(*) AS conflits_salle_ou_encadreur
FROM v_soutenances_conflits;

SELECT h.id, h.convention_id, h.ancien_statut, h.nouveau_statut,
       u.email AS auteur
FROM historique h
JOIN utilisateur u ON u.id = h.auteur_id
ORDER BY h.id;
