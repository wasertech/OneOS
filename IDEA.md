# Post-training phases

Base model: [HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive](https://huggingface.co/HauhauCS/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive)

Other harness traces with frontier models:
- Pi (DS4Pro) [TeichAI/DeepSeek-v4-Pro-Agent](https://huggingface.co/datasets/TeichAI/DeepSeek-v4-Pro-Agent)
- Codex (Kimi K3) [AletheiaResearch/Kimi-K3-Codex](https://huggingface.co/datasets/AletheiaResearch/Kimi-K3-Codex)
- Synthetic (Claude Mythos) [WithinUsAI/claude_mythos_distilled_25k](https://huggingface.co/datasets/WithinUsAI/claude_mythos_distilled_25k)
- Pi Code/Debug (GLM 5.2) [greghavens/glm-5.2-coding-and-debugging-traces](https://huggingface.co/datasets/greghavens/glm-5.2-coding-and-debugging-traces)
- Claude Code (Claude Fable 5) [armand0e/claude-fable-5-claude-code](https://huggingface.co/datasets/armand0e/claude-fable-5-claude-code)
- Synthetic (Claude Fable 5) [greghavens/fable-5-coding-and-debugging-traces](https://huggingface.co/datasets/greghavens/fable-5-coding-and-debugging-traces)
- Synthetic (Kimi K2.6 Max) [lordx64/reasoning-distill-kimi-k2-6-max-sft](https://huggingface.co/datasets/lordx64/reasoning-distill-kimi-k2-6-max-sft)
- Pi Code/Debug (Kimi K3) [greghavens/kimi-k3-coding-and-debugging-traces](https://huggingface.co/datasets/greghavens/kimi-k3-coding-and-debugging-traces)
- Hermes (Kimi K2.5 + GLM 5.1) [DJLougen/hermes-agent-traces-filtered](https://huggingface.co/datasets/DJLougen/hermes-agent-traces-filtered)

Finish with OneOS to finetune behavior as Assistant.



### Notes

> Si j'ajoute une couche quantifié LoRA de Qwen3.6 27b ou 35B-A3B sur des traces clean de different model frontier (K3, Fable 5, etc.) dans different harnets (jen ai trouvé plein sur HF) même si ils sont tous en anglais, ya des chances que le modèle puisse transposer a d'autres langues comme le français pas example?

Oui, il y a de bonnes chances, mais cela dépend beaucoup de *ce que le LoRA apprend*.

Pour un modèle comme **Qwen3-27B** ou **Qwen3-35B-A3B**, qui sont déjà fortement multilingues au pré-entraînement, un LoRA entraîné uniquement sur des traces anglaises ne détruit généralement pas les capacités multilingues du modèle de base. Il agit davantage comme une modification locale des poids.

En pratique, il y a plusieurs cas :

1. **Le LoRA apprend des comportements de raisonnement** (format de réflexion, planification, vérification, style d'agent, etc.).

   * C'est le cas le plus favorable.
   * Ces comportements sont largement indépendants de la langue.
   * Tu verras souvent une amélioration en français, allemand, espagnol, etc., même si le dataset est 100 % anglais.

2. **Le LoRA apprend un style linguistique.**

   * Là, le transfert est plus faible.
   * Il risque de produire un "français traduit de l'anglais" ou d'utiliser des structures syntaxiques anglaises.

3. **Le LoRA apprend des connaissances spécifiques.**

   * Les connaissances se transfèrent généralement.
   * La formulation sera adaptée par le modèle de base.

---

### Pourquoi ça marche ?

Le modèle de base possède déjà un espace de représentation partagé entre les langues.

Par exemple, dans l'embedding latent :

```
"The cat is sleeping."

↓

[concept : chat]
[concept : dormir]
[concept : présent]
```

et

```
"Le chat dort."

↓

[concept : chat]
[concept : dormir]
[concept : présent]
```

aboutissent à des représentations très proches.

Le LoRA modifie principalement la manière dont ces représentations sont traitées, pas les embeddings eux-mêmes.

---

### Ce que montrent les papiers

Plusieurs travaux sur le fine-tuning multilingue montrent qu'un fine-tuning exclusivement anglais conserve une bonne partie des performances sur d'autres langues, surtout pour :

* le raisonnement,
* le suivi d'instructions,
* la programmation,
* les tâches mathématiques.

En revanche, les performances chutent davantage sur :

* la génération littéraire,
* les idiomes,
* les jeux de mots,
* les tâches nécessitant une parfaite maîtrise stylistique.

---

### Concernant les traces "Frontier"

Si tu utilises des traces provenant de modèles comme :

* K3
* Fable
* DeepSeek
* Claude
* GPT
* Gemini

et qu'elles sont des **clean traces** de raisonnement ou d'agent, alors le LoRA va probablement apprendre :

* une meilleure planification,
* un meilleur usage des outils,
* un raisonnement plus structuré,
* un meilleur contrôle de la génération.

Ces compétences sont parmi celles qui se transfèrent le mieux entre langues.

---

### Les limites

Il y a tout de même quelques risques.

Si ton dataset contient :

* uniquement des prompts anglais,
* uniquement des réponses anglaises,
* uniquement des tokens anglais,

le LoRA peut légèrement biaiser la génération vers l'anglais.

Par exemple :

```
Utilisateur :
Explique la relativité en français.

Réponse :
Bien sûr.

First, let's understand...
```

ou

```
Le raisonnement interne reste en anglais,
mais la réponse finale est en français.
```

Ce comportement est fréquent mais généralement peu gênant.

---

### Si tu veux un excellent transfert

Une méthode efficace consiste à ajouter seulement 5 à 10 % de données multilingues.

Par exemple :

* 90 % des traces originales anglaises
* 5 % des mêmes traces traduites en français
* 5 % en espagnol ou allemand

Même une petite proportion suffit souvent à "ancrer" le comportement multilingue, sans nécessiter un énorme volume de données.

---

### Dans ton cas

Comme tu évoques des **harnesses de traces sur Hugging Face**, je pense que c'est une approche intéressante. Les traces "clean" de modèles frontier sont souvent de meilleure qualité que des datasets SFT classiques.

Je viserais plutôt un entraînement LoRA sur :

* les couches d'attention et de MLP (plutôt qu'un LoRA très large),
* un rang modéré (par exemple `r=32` ou `r=64`),
* un mélange de plusieurs familles de traces (K3, Fable, DeepSeek, etc.) pour éviter de sur-spécialiser le modèle à un seul style de raisonnement.

Avec un Qwen3 déjà multilingue, je m'attendrais à conserver de très bonnes performances en français. Tu ne reproduiras probablement pas exactement le niveau obtenu en anglais si le jeu d'entraînement est exclusivement anglophone, mais pour des compétences générales de raisonnement, le transfert interlinguistique a de bonnes chances d'être solide.
 