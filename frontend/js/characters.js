/**
 * StoryVerse AI — Character Forge Controller (characters.js)
 * ============================================================
 * Phase 7: Character Profile Bible (19 dimensions), psychological matrices,
 * multi-character ensemble concepts, and safe DOM manipulation.
 */

(function () {
  'use strict';

  // State
  let currentCharacterData = null;
  let currentVariationsData = null;
  let currentActiveMode = 'single'; // 'single' | 'variations'

  document.addEventListener('DOMContentLoaded', () => {
    // Studio Tabs
    const tabSingleChar = document.getElementById('tabSingleChar');
    const tabVariations = document.getElementById('tabVariations');
    const singleFormCard = document.getElementById('singleCharFormCard');
    const varFormCard = document.getElementById('variationsFormCard');

    // Single Character Form Elements
    const charForm = document.getElementById('characterForm');
    const descInput = document.getElementById('characterDescription');
    const nameInput = document.getElementById('charName');
    const genreInput = document.getElementById('charGenre');
    const roleInput = document.getElementById('charRole');
    const archetypeInput = document.getElementById('charArchetype');
    const ageInput = document.getElementById('charAge');
    const genderInput = document.getElementById('charGender');
    const langInput = document.getElementById('charLanguage');
    const toneInput = document.getElementById('charTone');
    const bgInput = document.getElementById('charBackground');
    const instructionsInput = document.getElementById('charInstructions');
    const generateCharBtn = document.getElementById('generateCharacterBtn');
    const descCounter = document.getElementById('charDescCounter');
    const characterValidationErrors = document.getElementById('characterValidationErrors');

    const clearCharacterValidationErrors = () => {
      if (!characterValidationErrors) return;
      characterValidationErrors.replaceChildren();
      characterValidationErrors.classList.remove('active');
    };

    const showCharacterValidationErrors = (errors) => {
      clearCharacterValidationErrors();
      if (!characterValidationErrors || !errors || typeof errors !== 'object') return [];

      const fieldLabels = {
        description: 'Character concept',
        genre: 'Genre',
        character_role: 'Narrative role',
        language: 'Language',
        tone: 'Tone',
        name: 'Character name',
        age: 'Age',
        gender: 'Gender',
        personality_type: 'Personality / archetype',
        background: 'Background',
        setting: 'Setting',
        additional_instructions: 'Creative directives'
      };
      const messages = [];
      const list = document.createElement('ul');

      Object.entries(errors).forEach(([field, message]) => {
        const detail = `${fieldLabels[field] || field}: ${message}`;
        messages.push(detail);
        const item = document.createElement('li');
        item.textContent = detail;
        list.appendChild(item);
      });

      if (messages.length) {
        characterValidationErrors.appendChild(list);
        characterValidationErrors.classList.add('active');
      }
      return messages;
    };

    [descInput, genreInput, roleInput, archetypeInput, ageInput, genderInput, langInput, toneInput, bgInput, instructionsInput]
      .forEach((input) => {
        if (input) {
          input.addEventListener('input', clearCharacterValidationErrors);
          input.addEventListener('change', clearCharacterValidationErrors);
        }
      });

    // Variations Form Elements
    const varForm = document.getElementById('variationsForm');
    const varPremiseInput = document.getElementById('varPremise');
    const varGenreInput = document.getElementById('varGenre');
    const varRoleInput = document.getElementById('varRole');
    const varCountInput = document.getElementById('varCount');
    const varLangInput = document.getElementById('varLanguage');
    const generateVarBtn = document.getElementById('generateVariationsBtn');
    const varPremiseCounter = document.getElementById('varPremiseCounter');
    const variationsValidationErrors = document.getElementById('variationsValidationErrors');

    const clearVariationsValidationErrors = () => {
      if (!variationsValidationErrors) return;
      variationsValidationErrors.replaceChildren();
      variationsValidationErrors.classList.remove('active');
    };

    const showVariationsValidationErrors = (errors) => {
      clearVariationsValidationErrors();
      if (!variationsValidationErrors || !errors || typeof errors !== 'object') return [];

      const fieldLabels = {
        premise: 'Story premise',
        story_context: 'Story premise',
        genre: 'Genre',
        count: 'Number of concepts',
        character_role: 'Focus role',
        language: 'Language'
      };
      const messages = [];
      const list = document.createElement('ul');

      Object.entries(errors).forEach(([field, message]) => {
        const detail = `${fieldLabels[field] || field}: ${message}`;
        messages.push(detail);
        const item = document.createElement('li');
        item.textContent = detail;
        list.appendChild(item);
      });

      if (messages.length) {
        variationsValidationErrors.appendChild(list);
        variationsValidationErrors.classList.add('active');
      }
      return messages;
    };

    [varPremiseInput, varGenreInput, varRoleInput, varCountInput, varLangInput].forEach((input) => {
      if (input) input.addEventListener('input', clearVariationsValidationErrors);
    });

    // Live Sidebar Summary Elements
    const summaryGenre = document.getElementById('summaryCharGenre');
    const summaryLang = document.getElementById('summaryCharLang');
    const summaryRole = document.getElementById('summaryCharRole');
    const summaryTone = document.getElementById('summaryCharTone');

    // Loading & Result Section Elements
    const loadingState = document.getElementById('characterLoadingState');
    const loadingTitle = document.getElementById('loadingTitle');
    const loadingSubtitle = document.getElementById('loadingSubtitle');
    const resultSection = document.getElementById('characterResultSection');

    // Result Header Elements
    const resultName = document.getElementById('resultCharName');
    const badgeRole = document.getElementById('resultRoleBadge');
    const badgeGenre = document.getElementById('resultGenreBadge');
    const badgeArchetype = document.getElementById('resultArchetypeBadge');
    const badgeAge = document.getElementById('resultAgeBadge');

    // View Mode Buttons & Containers
    const viewBibleBtn = document.getElementById('viewBibleBtn');
    const viewVariationsBtn = document.getElementById('viewVariationsBtn');
    const viewEditableBtn = document.getElementById('viewCharEditableBtn');
    const bibleView = document.getElementById('bibleView');
    const variationsContainer = document.getElementById('variationsContainer');
    const editableView = document.getElementById('charEditableView');
    const editableTextarea = document.getElementById('charEditableText');

    // Toolbar Buttons
    const copyBtn = document.getElementById('charCopyBtn');
    const regenerateBtn = document.getElementById('charRegenerateBtn');

    // Profile Bible Field Targets
    const valCoreWant = document.getElementById('valCoreWant');
    const valCoreNeed = document.getElementById('valCoreNeed');
    const valFatalFlaw = document.getElementById('valFatalFlaw');
    const valTheLie = document.getElementById('valTheLie');
    const valStrengths = document.getElementById('valStrengths');
    const valWeaknesses = document.getElementById('valWeaknesses');
    const valAppearance = document.getElementById('valAppearance');
    const valTraits = document.getElementById('valTraits');
    const valBackstory = document.getElementById('valBackstory');
    const valMotivations = document.getElementById('valMotivations');
    const valFears = document.getElementById('valFears');
    const valSecrets = document.getElementById('valSecrets');
    const valRelationships = document.getElementById('valRelationships');
    const valConflicts = document.getElementById('valConflicts');
    const valArc = document.getElementById('valArc');

    // ============================================================
    // 1. Studio Tab Switching
    // ============================================================
    function switchStudioTab(tab) {
      currentActiveMode = tab;
      if (tabSingleChar) tabSingleChar.classList.toggle('active', tab === 'single');
      if (tabVariations) tabVariations.classList.toggle('active', tab === 'variations');

      if (singleFormCard) singleFormCard.style.display = tab === 'single' ? 'block' : 'none';
      if (varFormCard) varFormCard.style.display = tab === 'variations' ? 'block' : 'none';

      updateSummary();
    }

    if (tabSingleChar) tabSingleChar.addEventListener('click', () => switchStudioTab('single'));
    if (tabVariations) tabVariations.addEventListener('click', () => switchStudioTab('variations'));

    // ============================================================
    // 2. Character Counters & Live Summary
    // ============================================================
    function updateCounters() {
      if (descInput && descCounter) descCounter.textContent = `${descInput.value.length} / 2000`;
      if (varPremiseInput && varPremiseCounter) varPremiseCounter.textContent = `${varPremiseInput.value.length} / 2000`;
    }

    function updateSummary() {
      if (currentActiveMode === 'single') {
        if (genreInput && summaryGenre) summaryGenre.textContent = genreInput.value;
        if (langInput && summaryLang) summaryLang.textContent = langInput.value;
        if (roleInput && summaryRole) summaryRole.textContent = roleInput.value;
        if (toneInput && summaryTone) summaryTone.textContent = toneInput.value;
      } else {
        if (varGenreInput && summaryGenre) summaryGenre.textContent = varGenreInput.value;
        if (varLangInput && summaryLang) summaryLang.textContent = varLangInput.value;
        if (varRoleInput && summaryRole) summaryRole.textContent = varRoleInput.value;
        if (summaryTone) summaryTone.textContent = 'Ensemble Diversity';
      }
    }

    if (descInput) descInput.addEventListener('input', updateCounters);
    if (varPremiseInput) varPremiseInput.addEventListener('input', updateCounters);
    if (genreInput) genreInput.addEventListener('change', updateSummary);
    if (langInput) langInput.addEventListener('change', updateSummary);
    if (roleInput) roleInput.addEventListener('change', updateSummary);
    if (toneInput) toneInput.addEventListener('change', updateSummary);
    if (varGenreInput) varGenreInput.addEventListener('change', updateSummary);
    if (varLangInput) varLangInput.addEventListener('change', updateSummary);
    if (varRoleInput) varRoleInput.addEventListener('change', updateSummary);

    updateCounters();
    updateSummary();

    // ============================================================
    // 3. View Mode Switching
    // ============================================================
    function switchResultView(mode) {
      if (viewBibleBtn) viewBibleBtn.classList.toggle('active', mode === 'bible');
      if (viewVariationsBtn) viewVariationsBtn.classList.toggle('active', mode === 'variations');
      if (viewEditableBtn) viewEditableBtn.classList.toggle('active', mode === 'editable');

      if (bibleView) bibleView.style.display = mode === 'bible' ? 'flex' : 'none';
      if (variationsContainer) variationsContainer.style.display = mode === 'variations' ? 'grid' : 'none';
      if (editableView) editableView.style.display = mode === 'editable' ? 'block' : 'none';
    }

    if (viewBibleBtn) viewBibleBtn.addEventListener('click', () => switchResultView('bible'));
    if (viewVariationsBtn) viewVariationsBtn.addEventListener('click', () => switchResultView('variations'));
    if (viewEditableBtn) viewEditableBtn.addEventListener('click', () => switchResultView('editable'));

    // ============================================================
    // 4. Form Submission — Generate Single Character Profile
    // ============================================================
    if (charForm) {
      charForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearCharacterValidationErrors();

        const description = descInput ? descInput.value.trim() : '';
        if (!description) {
          if (window.StoryVerse) window.StoryVerse.showToast('Please provide a character concept or dilemma.', 'warning');
          if (descInput) descInput.focus();
          return;
        }

        const payload = {
          description: description,
          character_name: nameInput && nameInput.value.trim() ? nameInput.value.trim() : null,
          genre: genreInput ? genreInput.value : 'Fantasy',
          character_role: roleInput ? roleInput.value : 'protagonist',
          character_archetype: archetypeInput && archetypeInput.value.trim() ? archetypeInput.value.trim() : null,
          age: ageInput && ageInput.value.trim() ? ageInput.value.trim() : null,
          gender: genderInput && genderInput.value.trim() ? genderInput.value.trim() : null,
          language: langInput ? langInput.value : 'English',
          tone: toneInput ? toneInput.value : 'Emotional',
          background: bgInput && bgInput.value.trim() ? bgInput.value.trim() : null,
          additional_instructions: instructionsInput && instructionsInput.value.trim() ? instructionsInput.value.trim() : null
        };

        // Loading state
        if (resultSection) resultSection.style.display = 'none';
        if (loadingState) {
          if (loadingTitle) loadingTitle.textContent = 'Forging 3D Character Profile...';
          if (loadingSubtitle) loadingSubtitle.textContent = 'Synthesizing psychological matrices, strengths, weaknesses, and narrative arc.';
          loadingState.style.display = 'block';
          loadingState.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        if (generateCharBtn) {
          generateCharBtn.disabled = true;
          const textSpan = generateCharBtn.querySelector('.btn-text');
          if (textSpan) textSpan.textContent = 'Forging Character...';
        }

        try {
          const res = await window.StoryVerseAPI.generateCharacter(payload);

          if (res && res.success && res.data) {
            currentCharacterData = res.data;
            renderCharacterBible(res.data);
            if (window.StoryVerse) {
              window.StoryVerse.showToast('👤 Character Profile forged successfully!', 'success');
            }
          } else {
            const errMsg = res?.message || 'Failed to generate character profile.';
            if (window.StoryVerse) window.StoryVerse.showToast(errMsg, 'error');
          }
        } catch (err) {
          console.error('Character generation failed:', err);
          const fieldErrors = showCharacterValidationErrors(err.errors);
          const message = fieldErrors.length
            ? fieldErrors.join(' ')
            : (err.message || 'Error generating character.');
          if (window.StoryVerse) window.StoryVerse.showToast(message, 'error');
        } finally {
          if (loadingState) loadingState.style.display = 'none';
          if (generateCharBtn) {
            generateCharBtn.disabled = false;
            const textSpan = generateCharBtn.querySelector('.btn-text');
            if (textSpan) textSpan.textContent = '👥 Forge Character Profile';
          }
        }
      });
    }

    // ============================================================
    // 5. Form Submission — Generate Character Variations
    // ============================================================
    if (varForm) {
      varForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearVariationsValidationErrors();

        const premise = varPremiseInput ? varPremiseInput.value.trim() : '';
        if (!premise) {
          showVariationsValidationErrors({ premise: 'Story premise is required.' });
          if (window.StoryVerse) window.StoryVerse.showToast('Please enter a story premise or conflict.', 'warning');
          if (varPremiseInput) varPremiseInput.focus();
          return;
        }

        const countVal = varCountInput ? varCountInput.valueAsNumber : 3;
        if (!Number.isInteger(countVal) || countVal < 2 || countVal > 5) {
          showVariationsValidationErrors({ count: 'Enter a whole number between 2 and 5.' });
          if (window.StoryVerse) window.StoryVerse.showToast('Concept count must be between 2 and 5.', 'warning');
          if (varCountInput) varCountInput.focus();
          return;
        }

        if (!varGenreInput || !varGenreInput.value) {
          showVariationsValidationErrors({ genre: 'Genre is required.' });
          if (window.StoryVerse) window.StoryVerse.showToast('Please select a genre.', 'warning');
          if (varGenreInput) varGenreInput.focus();
          return;
        }

        const payload = {
          premise: premise,
          genre: varGenreInput ? varGenreInput.value : 'Science Fiction',
          character_role: varRoleInput ? varRoleInput.value : 'Ensemble Cast',
          count: countVal,
          language: varLangInput ? varLangInput.value : 'English'
        };

        // Loading state
        if (resultSection) resultSection.style.display = 'none';
        if (loadingState) {
          if (loadingTitle) loadingTitle.textContent = 'Generating Ensemble Concepts...';
          if (loadingSubtitle) loadingSubtitle.textContent = 'Synthesizing diverse motivations, flaws, and archetypes.';
          loadingState.style.display = 'block';
          loadingState.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        if (generateVarBtn) {
          generateVarBtn.disabled = true;
          const textSpan = generateVarBtn.querySelector('.btn-text');
          if (textSpan) textSpan.textContent = 'Generating Concepts...';
        }

        try {
          const res = await window.StoryVerseAPI.generateCharacterVariations(payload);

          if (res && res.success && res.data) {
            currentVariationsData = res.data;
            renderVariationsResult(res.data);
            if (window.StoryVerse) {
              window.StoryVerse.showToast('🎭 Character concepts generated successfully!', 'success');
            }
          } else {
            const errMsg = res?.message || 'Failed to generate character variations.';
            if (window.StoryVerse) window.StoryVerse.showToast(errMsg, 'error');
          }
        } catch (err) {
          console.error('Character variations failed:', err);
          const fieldErrors = showVariationsValidationErrors(err.errors);
          const message = fieldErrors.length
            ? fieldErrors.join(' ')
            : (err.message || 'Error generating variations.');
          if (window.StoryVerse) window.StoryVerse.showToast(message, 'error');
        } finally {
          if (loadingState) loadingState.style.display = 'none';
          if (generateVarBtn) {
            generateVarBtn.disabled = false;
            const textSpan = generateVarBtn.querySelector('.btn-text');
            if (textSpan) textSpan.textContent = '🎭 Generate Ensemble Concepts';
          }
        }
      });
    }

    // ============================================================
    // 6. Safe DOM Renderers (XSS-Free)
    // ============================================================

    /**
     * Renders a 19-point Character Profile Bible.
     */
    function renderCharacterBible(data) {
      if (!data) return;

      // Header Banner
      if (resultName) resultName.textContent = data.character_name || 'Unnamed Character';
      if (badgeRole) badgeRole.textContent = data.character_role || 'Protagonist';
      if (badgeGenre) badgeGenre.textContent = data.metadata?.genre || 'Drama';
      if (badgeArchetype) badgeArchetype.textContent = data.character_archetype || 'Archetype';
      if (badgeAge) badgeAge.textContent = `Age: ${data.age || 'Adult'}`;

      // Psychological Matrix
      extractAndRenderPsychology(data);

      // Strengths & Weaknesses
      if (valStrengths) valStrengths.textContent = data.strengths || 'Not specified';
      if (valWeaknesses) valWeaknesses.textContent = data.weaknesses || 'Not specified';

      // Narrative Dimensions
      if (valAppearance) valAppearance.textContent = data.physical_appearance || 'Visual traits not detailed.';
      if (valTraits) valTraits.textContent = data.personality_traits || 'Personality traits not detailed.';
      if (valBackstory) valBackstory.textContent = data.backstory || 'Formative backstory not detailed.';
      if (valMotivations) valMotivations.textContent = data.motivations_and_goals || 'Goals not detailed.';
      if (valFears) valFears.textContent = data.fears || 'Fears not detailed.';
      if (valSecrets) valSecrets.textContent = data.secrets || 'Secrets not detailed.';
      if (valRelationships) valRelationships.textContent = data.relationships || 'Relationships not detailed.';

      // Combined Conflicts
      if (valConflicts) {
        const intC = data.internal_conflict ? `INTERNAL:\n${data.internal_conflict}` : '';
        const extC = data.external_conflict ? `EXTERNAL:\n${data.external_conflict}` : '';
        valConflicts.textContent = [intC, extC].filter(Boolean).join('\n\n') || 'Conflicts not specified.';
      }

      // Combined Arc & Role
      if (valArc) {
        const arc = data.character_arc ? `CHARACTER ARC:\n${data.character_arc}` : '';
        const roleStory = data.role_in_story ? `ROLE IN THE STORY:\n${data.role_in_story}` : '';
        valArc.textContent = [arc, roleStory].filter(Boolean).join('\n\n') || 'Arc not detailed.';
      }

      // Editable Full Profile Text
      if (editableTextarea) {
        editableTextarea.value = data.full_profile || '';
      }

      // Show results & set view to bible
      if (viewVariationsBtn) viewVariationsBtn.style.display = 'none';
      switchResultView('bible');
      if (resultSection) {
        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    /**
     * Extracts psychological quadrant parameters from structured fields or text.
     */
    function extractAndRenderPsychology(data) {
      let want = 'To achieve their overarching mission';
      let need = 'To face their hidden truth';
      let flaw = data.fatal_flaw || 'Hubris or lingering trauma';
      let lie = 'They must carry the burden alone';

      const psychText = data.psychological_profile || '';

      const wantM = psychText.match(/Core\s+Want[^\:]*?\:\s*([^\n]+)/i);
      if (wantM) want = wantM[1].trim();

      const needM = psychText.match(/Core\s+Need[^\:]*?\:\s*([^\n]+)/i);
      if (needM) need = needM[1].trim();

      const lieM = psychText.match(/Lie[^\:]*?\:\s*([^\n]+)/i);
      if (lieM) lie = lieM[1].trim();

      const flawM = psychText.match(/Fatal\s+Flaw[^\:]*?\:\s*([^\n]+)/i);
      if (flawM) flaw = flawM[1].trim();

      if (valCoreWant) valCoreWant.textContent = want;
      if (valCoreNeed) valCoreNeed.textContent = need;
      if (valFatalFlaw) valFatalFlaw.textContent = flaw;
      if (valTheLie) valTheLie.textContent = lie;
    }

    /**
     * Renders ensemble variations concept cards.
     */
    function renderVariationsResult(data) {
      if (!data || !variationsContainer) return;
      variationsContainer.replaceChildren(); // Safe clear

      // Header updates
      if (resultName) resultName.textContent = `Ensemble Concepts (${data.count || data.variations?.length || 3})`;
      if (badgeRole) badgeRole.textContent = 'Ensemble Cast';
      if (badgeGenre) badgeGenre.textContent = data.metadata?.genre || 'Drama';
      if (badgeArchetype) badgeArchetype.textContent = 'Multi-Concept';
      if (badgeAge) badgeAge.textContent = `${data.count || 3} Characters`;

      const variations = data.variations || [];
      variations.forEach((concept) => {
        const card = document.createElement('div');
        card.className = 'variation-concept-card';

        // Header
        const header = document.createElement('div');
        header.className = 'var-card-header';

        const nameBox = document.createElement('div');
        const nameP = document.createElement('div');
        nameP.className = 'var-concept-name';
        nameP.textContent = concept.name || `Concept ${concept.concept_number}`;
        nameBox.appendChild(nameP);

        const roleP = document.createElement('div');
        roleP.className = 'var-concept-role';
        roleP.textContent = `${concept.role} • ${concept.archetype}`;
        nameBox.appendChild(roleP);
        header.appendChild(nameBox);
        card.appendChild(header);

        // Logline / Hook
        if (concept.logline) {
          const loglineP = document.createElement('div');
          loglineP.className = 'var-logline';
          loglineP.textContent = concept.logline;
          card.appendChild(loglineP);
        }

        // Meta list (Motivation, Flaw, Trait)
        const metaList = document.createElement('div');
        metaList.className = 'var-meta-list';

        if (concept.motivation) {
          const item = document.createElement('div');
          item.className = 'var-meta-item';
          const strong = document.createElement('strong');
          strong.textContent = 'Motivation: ';
          const span = document.createElement('span');
          span.textContent = concept.motivation;
          item.appendChild(strong);
          item.appendChild(span);
          metaList.appendChild(item);
        }

        if (concept.fatal_flaw) {
          const item = document.createElement('div');
          item.className = 'var-meta-item';
          const strong = document.createElement('strong');
          strong.textContent = 'Fatal Flaw: ';
          const span = document.createElement('span');
          span.textContent = concept.fatal_flaw;
          item.appendChild(strong);
          item.appendChild(span);
          metaList.appendChild(item);
        }

        if (concept.key_trait) {
          const item = document.createElement('div');
          item.className = 'var-meta-item';
          const strong = document.createElement('strong');
          strong.textContent = 'Key Feature: ';
          const span = document.createElement('span');
          span.textContent = concept.key_trait;
          item.appendChild(strong);
          item.appendChild(span);
          metaList.appendChild(item);
        }

        card.appendChild(metaList);

        // Action Button: Forge Deep Profile from this concept
        const expandBtn = document.createElement('button');
        expandBtn.className = 'btn btn-secondary btn-sm var-expand-btn';
        expandBtn.textContent = '⚡ Forge 3D Profile for This Character';
        expandBtn.addEventListener('click', () => {
          // Switch to single tab
          switchStudioTab('single');
          if (descInput) {
            descInput.value = `${concept.name} (${concept.role}, ${concept.archetype}): ${concept.logline}. Motivation: ${concept.motivation}. Flaw: ${concept.fatal_flaw}`;
            updateCounters();
          }
          if (nameInput) nameInput.value = concept.name;
          if (archetypeInput) archetypeInput.value = concept.archetype;
          if (charForm) {
            charForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
          }
        });

        card.appendChild(expandBtn);
        variationsContainer.appendChild(card);
      });

      // Editable View
      if (editableTextarea) {
        editableTextarea.value = data.full_text || '';
      }

      // Show variations tab in results
      if (viewVariationsBtn) viewVariationsBtn.style.display = 'block';
      switchResultView('variations');
      if (resultSection) {
        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    // ============================================================
    // 7. Action Toolbar Handlers
    // ============================================================
    if (copyBtn) {
      copyBtn.addEventListener('click', async () => {
        const textToCopy = editableTextarea && editableTextarea.value.trim()
          ? editableTextarea.value.trim()
          : (currentCharacterData?.full_profile || currentVariationsData?.full_text || '');

        if (!textToCopy) {
          if (window.StoryVerse) window.StoryVerse.showToast('No character text to copy.', 'warning');
          return;
        }

        try {
          await navigator.clipboard.writeText(textToCopy);
          if (window.StoryVerse) window.StoryVerse.showToast('📋 Character profile copied to clipboard!', 'success');
        } catch (err) {
          if (editableTextarea) {
            editableTextarea.select();
            document.execCommand('copy');
            if (window.StoryVerse) window.StoryVerse.showToast('📋 Profile copied!', 'success');
          }
        }
      });
    }

    if (regenerateBtn) {
      regenerateBtn.addEventListener('click', () => {
        if (currentActiveMode === 'single' && charForm) {
          charForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        } else if (currentActiveMode === 'variations' && varForm) {
          varForm.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        }
      });
    }

    // Save as Project
    const saveProjectBtn = document.getElementById('charSaveProjectBtn');
    if (saveProjectBtn) {
      saveProjectBtn.addEventListener('click', async () => {
        const charName = document.getElementById('resultCharName')?.textContent.trim() || 'Character Profile';
        const content = editableTextarea && editableTextarea.value.trim()
          ? editableTextarea.value.trim()
          : (currentCharacterData?.full_profile || currentVariationsData?.full_text || '');

        if (!content) {
          if (window.StoryVerse) window.StoryVerse.showToast('No character profile generated yet to save.', 'warning');
          return;
        }

        saveProjectBtn.disabled = true;
        try {
          const res = await window.StoryVerseAPI.createProject({
            title: `${charName} — Character Bible`,
            content_type: 'character',
            genre: genreSelect ? genreSelect.value : undefined,
            language: langSelect ? langSelect.value : 'English',
            description: descInput ? descInput.value.trim() : undefined,
            content: content
          });

          if (res.success && res.data) {
            if (window.StoryVerse) {
              window.StoryVerse.showToast(`Character bible saved to portfolio! Project #${res.data.id}`, 'success');
            }
          } else {
            throw new Error(res.message || 'Failed to save project.');
          }
        } catch (err) {
          if (window.StoryVerse) window.StoryVerse.showToast(err.message || 'Error saving project.', 'error');
        } finally {
          saveProjectBtn.disabled = false;
        }
      });
    }

    // Export dropdown toggle + per-format download
    const charExportBtn = document.getElementById('charExportBtn');
    const charExportMenu = document.getElementById('charExportMenu');
    if (charExportBtn && charExportMenu) {
      charExportBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        charExportMenu.style.display = charExportMenu.style.display === 'none' ? 'flex' : 'none';
      });
      document.addEventListener('click', () => { charExportMenu.style.display = 'none'; });

      charExportMenu.querySelectorAll('.dropdown-item').forEach(item => {
        item.addEventListener('click', async () => {
          const format = item.dataset.format;
          charExportMenu.style.display = 'none';
          const charName = document.getElementById('resultCharName')?.textContent.trim() || 'Character';
          const title = `${charName} — Character Bible`;
          const content = editableTextarea && editableTextarea.value.trim()
            ? editableTextarea.value.trim()
            : (currentCharacterData?.full_profile || currentVariationsData?.full_text || '');
          if (!content) {
            if (window.StoryVerse) window.StoryVerse.showToast('No character profile content to export.', 'warning');
            return;
          }
          item.disabled = true;
          try {
            if (window.StoryVerse) window.StoryVerse.showToast(`Preparing ${format.toUpperCase()} download...`, 'info');
            await window.StoryVerseAPI.exportDocument(format, {
              title: title,
              content: content,
              project_type: 'character',
              genre: (genreInput ? genreInput.value : undefined),
              language: (langInput ? langInput.value : 'English')
            });
            if (window.StoryVerse) window.StoryVerse.showToast(`${format.toUpperCase()} downloaded successfully!`, 'success');
          } catch (err) {
            if (window.StoryVerse) window.StoryVerse.showToast(err.message || 'Export failed.', 'error');
          } finally {
            item.disabled = false;
          }
        });
      });
    }
  });
})();
