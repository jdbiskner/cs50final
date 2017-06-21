import nltk
import token 

class Analyzer():
    """Implements sentiment analysis."""

    def __init__(self, positives, negatives):
        """Initialize Analyzer."""
        # create both lists; may not be needed
        self.poslist = list()
        self.neglist = list()
       
        # create list of positive words
        with open(positives) as lines:
            for line in lines:
                if not line.startswith(';'):
                    self.poslist.append(str.strip(line))
        
        # create list of negative words    
        with open(negatives) as lines:   
            for line in lines:
                if not line.startswith(';'):
                    self.neglist.append(str.strip(line))

    def analyze(self, text):
        """Analyze text for sentiment, returning its score."""
    
        # instantiate tokenizer
        tokenizer = nltk.tokenize.TweetTokenizer(preserve_case=False)
        
        # pass text to tokenizer
        tokens = tokenizer.tokenize(text)
        
        # prepare score for usage in loops
        score = 0    
        
        # iterate through the text, adjusting score
        for token in tokens:
            if token in self.poslist:
                score += 1
            elif token in self.neglist:
                score -= 1
            
        return score
