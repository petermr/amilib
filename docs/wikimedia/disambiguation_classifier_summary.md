# Disambiguation Classifier - User Summary

## 🎯 What This System Does

The **Disambiguation Classifier** automatically identifies which Wikipedia disambiguation options are most relevant to your specific subject area. Instead of manually reading through all options, it uses your existing **AmiDictionary** to score and rank them by relevance.

## 🔍 The Problem It Solves

When you search for terms like "GHG" on Wikipedia, you get multiple options:

- **Greenhouse gas** - A gas that absorbs and emits radiant energy
- **General Healthcare Group** - A British healthcare company  
- **George H. Goble** - Staff member at Purdue University
- **Gruppenhorchgerät** - A hydrophone array used on Nazi U-boats
- **Marshfield Municipal Airport** - An airport in Massachusetts

**Without classification**: You have to read through all 5 options to find the climate-related one.

**With classification**: The system automatically identifies "Greenhouse gas" as highly relevant to climate topics.

## 🛠️ How It Works

### **Step 1: Your Dictionary Provides the Vocabulary**
The system uses your **AmiDictionary** entries as the source of relevant terms:

```python
# Your climate dictionary contains:
- "climate change"
- "greenhouse gas" 
- "carbon dioxide"
- "emissions"
- "temperature"
# ... and many more climate-related terms
```

### **Step 2: Automatic Scoring**
For each disambiguation option, the system:

1. **Extracts the text** (e.g., "Greenhouse gas, a gas that absorbs...")
2. **Checks for matches** against your dictionary terms
3. **Scores the relevance** based on matches found
4. **Ranks the options** from most to least relevant

### **Step 3: Smart Classification**
Options are automatically classified as:

- **🟢 Highly Relevant** - Multiple dictionary term matches
- **🟡 Moderately Relevant** - Some dictionary term matches  
- **🔴 Not Relevant** - No dictionary term matches

## 📊 Example Results

Using a climate-focused dictionary, here's how "GHG" disambiguation would be classified:

| **Option** | **Dictionary Matches** | **Score** | **Classification** |
|------------|------------------------|-----------|-------------------|
| **Greenhouse gas** | ["greenhouse gas", "gas", "absorbs", "emits"] | **8.5** | 🟢 Highly Relevant |
| General Healthcare Group | [] | **0.0** | 🔴 Not Relevant |
| George H. Goble | [] | **0.0** | 🔴 Not Relevant |
| Gruppenhorchgerät | [] | **0.0** | 🔴 Not Relevant |
| Marshfield Municipal Airport | [] | **0.0** | 🔴 Not Relevant |

## 🚀 How to Use It

### **Basic Usage**

```python
from amilib.ami_dict import AmiDictionary
from amilib.disambiguation_classifier import DisambiguationClassifier

# Load your dictionary
climate_dict = AmiDictionary.create_from_xml_file("climate_dictionary.xml")

# Create classifier
classifier = DisambiguationClassifier(climate_dict)

# Classify disambiguation options
disambiguation_options = wikipedia_page.get_disambiguation_list()
classified_results = classifier.classify_options(disambiguation_options)

# Get the most relevant option
best_option = classified_results[0]
print(f"Most relevant: {best_option['text']}")
print(f"Relevance score: {best_option['score']}")
```

### **Advanced Usage with Custom Weights**

```python
# Configure classification for your domain
config = {
    'term_weight': 0.6,        # How much to weight exact term matches
    'description_weight': 0.3,  # How much to weight description text
    'synonym_weight': 0.1,     # How much to weight synonyms
    'threshold_high': 5.0,     # Score needed for "highly relevant"
    'threshold_moderate': 2.0  # Score needed for "moderately relevant"
}

classifier = DisambiguationClassifier(climate_dict, config=config)
```

## 🎨 Customization Options

### **1. Domain-Specific Dictionaries**
Create different dictionaries for different subject areas:

- **Climate Science**: `climate_dictionary.xml`
- **Healthcare**: `healthcare_dictionary.xml`  
- **Technology**: `tech_dictionary.xml`
- **Finance**: `finance_dictionary.xml`

### **2. Scoring Adjustments**
Fine-tune how the system weights different types of matches:

```python
# Example: Healthcare domain might weight descriptions more heavily
healthcare_config = {
    'term_weight': 0.5,        # Lower weight for terms
    'description_weight': 0.4,  # Higher weight for descriptions
    'synonym_weight': 0.1      # Same weight for synonyms
}
```

### **3. Threshold Customization**
Adjust what scores qualify as "relevant":

```python
# For strict classification (fewer false positives)
strict_config = {
    'threshold_high': 7.0,      # Higher bar for "highly relevant"
    'threshold_moderate': 4.0   # Higher bar for "moderately relevant"
}

# For lenient classification (more potential matches)
lenient_config = {
    'threshold_high': 3.0,      # Lower bar for "highly relevant"
    'threshold_moderate': 1.0   # Lower bar for "moderately relevant"
}
```

## 🔧 Technical Details

### **What Gets Scored**

1. **Exact Term Matches**: Dictionary terms found in disambiguation text
2. **Description Content**: Text from dictionary entry descriptions
3. **Synonyms**: Alternative terms for dictionary entries
4. **Partial Matches**: Substrings and related terms

### **Scoring Algorithm**

```
Total Score = (Term Matches × 0.6) + (Description Matches × 0.3) + (Synonym Matches × 0.1)
```

### **Performance Characteristics**

- **Speed**: Fast keyword matching (O(n) where n is text length)
- **Memory**: Efficient vocabulary lookup using sets
- **Scalability**: Works with dictionaries of any size
- **Accuracy**: Improves as your dictionary improves

## 📈 Benefits

### **For Researchers**
- **Save Time**: No more manual reading of irrelevant options
- **Improve Accuracy**: Consistent classification across multiple searches
- **Focus Attention**: Spend time on relevant content, not filtering

### **For Developers**
- **No New Dependencies**: Uses existing AmiDictionary infrastructure
- **Easy Integration**: Simple API that fits existing workflows
- **Extensible**: Easy to add new domains and scoring methods

### **For Organizations**
- **Standardize Classification**: Consistent results across teams
- **Improve Efficiency**: Faster content discovery and analysis
- **Reduce Errors**: Fewer missed relevant options

## 🚨 Limitations & Considerations

### **Current Limitations**
1. **Dictionary Dependent**: Quality depends on your dictionary content
2. **Language Specific**: Currently English-only
3. **Context Blind**: Doesn't understand semantic relationships
4. **Manual Fallback**: Users must handle cases with no matches

### **When It Works Best**
- ✅ **Well-curated dictionaries** with comprehensive coverage
- ✅ **Clear domain boundaries** (climate vs. healthcare)
- ✅ **Consistent terminology** across your subject area
- ✅ **Regular dictionary updates** as new terms emerge

### **When It Needs Help**
- ⚠️ **New domains** without existing dictionaries
- ⚠️ **Ambiguous terms** that span multiple domains
- ⚠️ **Rapidly evolving** terminology
- ⚠️ **Cross-domain** concepts

## 🔮 Future Enhancements

### **Planned Improvements**
1. **Machine Learning**: Learn from user feedback to improve scoring
2. **Semantic Analysis**: Understand meaning, not just word matches
3. **Multi-language Support**: Extend beyond English
4. **Automatic Dictionary Building**: Suggest new terms based on usage

### **User Feedback Integration**
- **Mark Results**: Rate classification accuracy
- **Suggest Improvements**: Add missing terms or adjust weights
- **Domain Adaptation**: Learn your specific use cases
- **Performance Tracking**: Monitor classification success rates

## 💡 Best Practices

### **1. Build Quality Dictionaries**
- Include **core terms** for your domain
- Add **synonyms** and **alternative spellings**
- Include **descriptions** with relevant context
- **Regular updates** as terminology evolves

### **2. Test with Real Examples**
- Try classification with **known disambiguation pages**
- **Verify results** against your domain knowledge
- **Adjust thresholds** based on your needs
- **Collect feedback** on classification accuracy

### **3. Monitor Performance**
- Track **classification success rates**
- Identify **frequently missed terms**
- **Update dictionaries** based on gaps
- **Share feedback** to improve the system

## 🆘 Getting Help

### **Common Issues**
1. **No matches found**: Your dictionary may need more terms
2. **Too many false positives**: Adjust thresholds higher
3. **Missing relevant options**: Lower thresholds or add more terms
4. **Slow performance**: Optimize dictionary size and structure

### **Support Resources**
- **Documentation**: Check the technical implementation guide
- **Examples**: Review sample dictionaries and configurations
- **Community**: Share experiences and best practices
- **Feedback**: Report issues and suggest improvements

## 🎯 Quick Start Checklist

- [ ] **Create or load** your AmiDictionary
- [ ] **Test classification** with known disambiguation pages
- [ ] **Adjust thresholds** to match your needs
- [ ] **Integrate** into your existing workflow
- [ ] **Monitor results** and provide feedback
- [ ] **Update dictionary** based on gaps and new terms

---

**The Disambiguation Classifier transforms Wikipedia's overwhelming options into focused, relevant results using your existing knowledge base. Start with a good dictionary, test with real examples, and watch your content discovery efficiency soar!**
