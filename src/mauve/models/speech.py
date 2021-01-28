from mauve.constants import SPEECH_QUOTES


class Speech():

    def __init__(
        self,
        text=None,
        segments=None,
        speaker=None,
        inflection=None
    ):
        '''

        :kwarg text: The text of the speech
        :kwarg segments: The segments of the speech.
            Can prob replace text with this parsed
        :kwarg speaker: the identifier of the speaker
        :kwarg inflection: said / exclaimed / however someone said the speech.
            Should rename to something verby
        '''
        self.segments = segments
        self._text = text
        self.speaker = speaker
        self._inflection = inflection

    @property
    def sentences(self):
        # the sentences of the text since there can be multiple
        # sentences from quote_aware_sent_tokenize
        return

    @property
    def text(self):
        if self._text is not None:
            return self._text
        return ' '.join([s.text for s in self.segments])

    @property
    def inflection(self):
        inflection = None
        if self._inflection:
            inflection = self._inflection
        return inflection

    def serialize(self):
        return {
            'text': self.text,
            'speaker': self.speaker,
            'inflection': self.inflection,
        }


def extract_speech(sentence):

    speech_words = ['said', 'says', 'exclaimed', 'whispered', 'wrote', 'continued', 'told', 'shouted', 'called', 'recalled', 'explained', 'admitted', 'remarked', 'bellowed', 'shrieked', 'told', 'ask', 'asked', 'confided', 'fulminated', 'mused', 'rejoined', 'cried', 'panted', 'continued', 'ejaculated', 'replied', 'interrupted', 'remarked', 'declared', 'queried', 'repeated', 'added', 'lied', 'insisted', 'answered']
    speakers = ['he', 'they', 'she', 'I', 'we']

    within = False
    within_section = []
    broken_idx = -1
    start_speech_idx = -1

    # Some books do:
    # He said 'Yah yah yah.' And what did that mean?

    # said the cat, the cat said. We should shuffle and use only one I guess for handiness sake?

    # starting idx would be handy for he said "shut up"
    for idx, segment in enumerate(sentence.segments):
        if segment.text in SPEECH_QUOTES and within:
            within = False
            broken_idx = idx
            break  # allow for multiple once one works

        if within:
            within_section.append(segment)

        if segment.text in SPEECH_QUOTES and not within:
            start_speech_idx = idx
            within = True

    if not within_section:
        return

    after_speech = sentence.segments[broken_idx + 1:broken_idx + 4]
    pre_speech = sentence.segments[max(start_speech_idx - 4, 0):max(start_speech_idx, 0)]

    inflection = None
    speaker = None

    for interesting_part in [after_speech, pre_speech]:

        inflection_intersection = set([f.text.lower() for f in interesting_part]).intersection(set(speech_words))
        if inflection_intersection != set():
            # handle if multiple
            inflection = list(inflection_intersection)[0]

        speaker_intersection = set([f.text.lower() for f in interesting_part]).intersection(set(speakers))
        if speaker_intersection != set():
            # handle if multiple
            # also check for names, not just pronouns
            speaker = list(speaker_intersection)[0]

        for i in interesting_part:
            if i.is_person:
                speaker = i.text

        # if we have a name, that's a better speaker

    return Speech(
        segments=within_section,
        speaker=speaker,
        inflection=inflection
    )
