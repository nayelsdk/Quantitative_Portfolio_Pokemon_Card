# Portfolio Pokemon Cards ⚡

This projects aims to build a potfolio based on pokemon cards and the secondary market. You will be able to buy a deck of cards that have a concrete probability to make profit after months/years.

## Here are the main objectives of the projet : 

- Récolter les données grâce au site internet TCGPlayer (un site qui répertorie le marché secondaire des cartes anglaises). Nous selectionnerons ensuite les paramètres les plus pertinents.

- Nous prédirons le prix des cartes Pokémon grâce à deux méthodes essentiellement :
  - Des modèles de régression (régression linéaire, multiple, XGBoost) afin de définir les différentes caractéristiques qui donnent de la valeur ou non pour une carte.
  - Un modèle de prédiction de Série Temporelles grâce aux ventes précédentes

- L'étape suivante serait de déterminer les espérances de gain pour chaque cartes ainsi que meur volatilité possible au fil du temps

- Créer une interface (via Streamlit pour le moment) qui sera un conseiller d'investissement pour les cartes Pokémon, il comportera :
  - Le montant que l'on souhaite investir
  - La mentalité de l'investisseur - gagner peu mais peu de volatilité ou bien averse au risque

- Il renverra les cartes qu'il faudra acheter et la date prévisionnelle de vente.
