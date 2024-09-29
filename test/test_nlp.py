"""
Tests for NLP
"""
import unittest
from pathlib import Path
import csv

from pytest import approx

from amilib.file_lib import FileLib
from amilib.util import Util
from test.resources import Resources
from test.test_all import AmiAnyTest

from amilib.ami_nlp import AmiNLP, AmiRake

import nltk
nltk.download('stopwords')

logger = Util.get_logger(__name__)

class NLPTest(AmiAnyTest):
    """
    Tests for ami_nlp
    """
    # import nltk, string

    @unittest.skip("needs installation")
    def test_compute_text_similarity_STAT(self):
        """
        ami_nlp,cosine_sim compares strings
        :return:
        """
        ami_nlp = AmiNLP()
        assert ami_nlp.cosine_sim('a little bird', 'a little bird') == approx(1.0)
        assert ami_nlp.cosine_sim('a little bird', 'a little bird chirps') == approx(0.7093, abs=0.001)
        assert ami_nlp.cosine_sim('a little bird', 'a big dog barks') == approx(0, abs=0.001)

    @unittest.skip("crashes on PMR machine with 'illegal instruction' - probably incompatible hardware")
    def test_keyBERT(self):
        """
        from keyBERT docs
        """
        logger.info("start")
        from keybert import KeyBERT

        doc = """
                 Supervised learning is the machine learning task of learning a function that
                 maps an input to an output based on example input-output pairs. It infers a
                 function from labeled training data consisting of a set of training examples.
                 In supervised learning, each example is a pair consisting of an input object
                 (typically a vector) and a desired output value (also called the supervisory signal).
                 A supervised learning algorithm analyzes the training data and produces an inferred function,
                 which can be used for mapping new examples. An optimal scenario will allow for the
                 algorithm to correctly determine the class labels for unseen instances. This requires
                 the learning algorithm to generalize from the training data to unseen situations in a
                 'reasonable' way (see inductive bias).
              """
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(doc)
        assert keywords is not None

    def test_rake_nltk(self):
        """
        example from repo/pypi
        """
        ami_rake = AmiRake()

        doc = """
                 Supervised learning is the machine learning task of learning a function that
                 maps an input to an output based on example input-output pairs. It infers a
                 function from labeled training data consisting of a set of training examples.
                 In supervised learning, each example is a pair consisting of an input object
                 (typically a vector) and a desired output value (also called the supervisory signal).
                 A supervised learning algorithm analyzes the training data and produces an inferred function,
                 which can be used for mapping new examples. An optimal scenario will allow for the
                 algorithm to correctly determine the class labels for unseen instances. This requires
                 the learning algorithm to generalize from the training data to unseen situations in a
                 'reasonable' way (see inductive bias).
              """
        ami_rake.read_text(doc)
        ranked_phrases = ami_rake.get_ranked_phrases()
        assert ranked_phrases == [
    'see inductive bias ).',
 'labeled training data consisting',
 'supervised learning algorithm analyzes',
 'supervisory signal ).',
 'mapping new examples',
 'machine learning task',
 'desired output value',
 'training data',
 'training data',
 'training examples',
 'supervised learning',
 'supervised learning',
 'pair consisting',
 'learning algorithm',
 'output pairs',
 'output based',
 'unseen situations',
 'unseen instances',
 'optimal scenario',
 'correctly determine',
 'class labels',
 'also called',
 'input object',
 'inferred function',
 'example input',
 'learning',
 'algorithm',
 'input',
 'example',
 'function',
 'function',
 'way',
 'vector',
 'used',
 'typically',
 'set',
 'requires',
 'reasonable',
 'produces',
 'maps',
 'infers',
 'generalize',
 'allow']

        ranked_phrases_with_scores = ami_rake.get_ranked_phrases_with_scores()
        assert ranked_phrases_with_scores == [
 (15.5, 'see inductive bias ).'),
 (12.166666666666666, 'labeled training data consisting'),
 (11.333333333333334, 'supervised learning algorithm analyzes'),
 (9.5, 'supervisory signal ).'),
 (8.5, 'mapping new examples'),
 (8.333333333333334, 'machine learning task'),
 (8.333333333333334, 'desired output value'),
 (5.166666666666666, 'training data'),
 (5.166666666666666, 'training data'),
 (5.0, 'training examples'),
 (5.0, 'supervised learning'),
 (5.0, 'supervised learning'),
 (5.0, 'pair consisting'),
 (4.666666666666667, 'learning algorithm'),
 (4.333333333333334, 'output pairs'),
 (4.333333333333334, 'output based'),
 (4.0, 'unseen situations'),
 (4.0, 'unseen instances'),
 (4.0, 'optimal scenario'),
 (4.0, 'correctly determine'),
 (4.0, 'class labels'),
 (4.0, 'also called'),
 (3.666666666666667, 'input object'),
 (3.333333333333333, 'inferred function'),
 (3.166666666666667, 'example input'),
 (2.3333333333333335, 'learning'),
 (2.3333333333333335, 'algorithm'),
 (1.6666666666666667, 'input'),
 (1.5, 'example'),
 (1.3333333333333333, 'function'),
 (1.3333333333333333, 'function'),
 (1.0, 'way'),
 (1.0, 'vector'),
 (1.0, 'used'),
 (1.0, 'typically'),
 (1.0, 'set'),
 (1.0, 'requires'),
 (1.0, 'reasonable'),
 (1.0, 'produces'),
 (1.0, 'maps'),
 (1.0, 'infers'),
 (1.0, 'generalize'),
 (1.0, 'allow')]

    def test_rake_wg3_chap03_exec_summ(self):
        """
        IPCC WG3 Chapter03
        """
        text = """
        Chapter 3 assesses the emissions pathways literature in order to identify their key characteristics (both in commonalities and differences) and to understand how societal choices may steer the system into a particular direction (high confidence) . More than 2000 quantitative emissions pathways were submitted to the IPCC’s Sixth Assessment Report AR6 scenarios database, out of which 1202 scenarios included sufficient information for assessing the associated warming consistent with WGI. Five Illustrative Mitigation Pathways (IMPs) were selected, each emphasising a different scenario element as its defining feature: heavy reliance on renewables (IMP-Ren), strong emphasis on energy demand reductions (IMP-LD), extensive use of carbon dioxide removal (CDR) in the energy and the industry sectors to achieve net negative emissions (IMP-Neg), mitigation in the context of broader sustainable development (IMP-SP), and the implications of a less rapid and gradual strengthening of near-term mitigation actions (IMP-GS). {3.2, 3.3}
Pathways consistent with the implementation and extrapolation of countries’ implemented policies until the end of 2020 see greenhouse gas (GHG) emissions reaching 54–61GtCO2-eq yr–1 by 2030 and to 47–67 GtCO2-eq yr–1 by 2050, leading to a median global warming of 2.2°C to 3.5°C by 2100 (medium confidence). These pathways consider policies at the time that they were developed. The Shared Socio-economic Pathways (SSPs) permit a more systematic assessment of future GHG emissions and their uncertainties than was possible in AR5. The main emissions drivers include growth in population, reaching 8.5–9.7 billion by 2050, and an increase in global GDP of 2.7–4.1% per year between 2015 and 2050. Final energy demand in the absence of any new climate policies is projected to grow to around 480–750 EJ yr –1 in 2050 (compared to around 390 EJ in 2015) (medium confidence). The highest emissions scenarios in the literature result in global warming of >5°C by 2100, based on assumptions of rapid economic growth and pervasive climate policy failures ( high conf idence). {3.3}
Many pathways in the literature show how tolimit global warming compared to pre-industrial times to 2°C (>67%) with no overshoot or to limit warming to 1.5°C (>50%) with no or limited overshoot. The likelihood of limiting warming to 1.5°C with no or limited overshoot has dropped in AR6 compared to theSpecial Report on Global Warming of 1.5°C (SR1.5) because global GHG emissions have risen since the time SR1.5 was published, leading to higher near-term emissions (2030) and higher cumulative CO2 emissions until the time of net zero (medium confidence) . Only a small number of published pathways limit global warming to 1.5°C without overshoot over the course of the 21st century. {3.3, Annex III.II.3}
Cost-effective mitigation pathways assuming immediate action1 tolimit warming to 2°C (>67%) are associated with net global GHG emissions of 30–49GtCO2-eq yr–1by 2030 and 14–26GtCO2-eq yr–1by 2050 (medium confidence). This corresponds to reductions, relative to 2019 levels, of 13–45% by 2030 and 52–76% by 2050. Pathways that limit global warming to below 1.5°C with no or limited overshoot require a further acceleration in the pace of the transformation, with net GHG emissions typically around 21–36 GtCO2-eq yr –1 by 2030 and 1–15 GtCO2-eq yr –1 by 2050; thus, reductions of 34–60% by 2030 and 73–98% by 2050 relative to 2019 levels. {3.3}
Pathways following Nationally Determined Contributions (NDCs) announced prior to COP262 until 2030 reach annual emissions of 47–57GtCO2-eq by 2030, thereby making it impossible to limit warming to 1.5°C with no or limited overshoot and strongly increasing the challenge to limit warming to 2°C (>67%) (high confidence). A high overshoot of 1.5°C increases the risks from climate impacts and increases the dependence on large-scale carbon dioxide removal from the atmosphere. A future consistent with NDCs announced prior to COP26 implies higher fossil fuel deployment and lower reliance on low-carbon alternatives until 2030, compared to mitigation pathways with immediate action to limit warming to 2°C (>67%) or lower. To limit warming to 2°C (>67%) after following the NDCs to 2030, the pace of global GHG emission reductions would need to accelerate rapidly from 2030 onward: to an average of 1.4–2.0 GtCO2-eq yr –1 between 2030 and 2050, which is around two-thirds of the global CO2 emission reductions in 2020 due to the COVID-19 pandemic, and around 70% faster than in immediate action pathways that limit warming to 2°C (>67%). Accelerating emission reductions after following an NDC pathway to 2030 would be particularly challenging because of the continued buildup of fossil fuel infrastructure that would be expected to take place between now and 2030. {3.5, 4.2}
Pathways accelerating actions compared to NDCs announced prior to COP26 that reduce annual GHG emissions to48 (38–52) GtCO2-eqby 2030, or 2–9GtCO2-eq below projected emissions from fully implementing NDCs announced prior to COP26, reduce the mitigation challenge forlimiting warming to 2°C (>67%) after 2030 (medium confidence). The accelerated action pathways are characterised by a global, but regionally differentiated, roll out of regulatory and pricing policies. Compared to NDCs, they see less fossil fuels and more low-carbon fuels until 2030, and narrow, but do not close the gap to pathways assuming immediate global action using all available least-cost abatement options. All delayed or accelerated action pathways that limit warming to 2°C (>67%) converge to a global mitigation regime at some point after 2030 by putting a significant value on reducing carbon and other GHG emissions in all sectors and regions. {3.5}
Mitigation pathways limiting warming to 1.5°C (>50%) with no or limited overshoot reach 50% reductions of CO2 in the 2030s, relative to 2019, then reduce emissions further to reach net zero CO2 emissions in the 2050s. Pathwayslimiting warming to 2°C (>67%) reach 50% reductions in the 2040s and net zero CO2by 2070s (medium confidence). {3.3, Cross-Chapter Box 3 in this chapter}
Peak warming in mitigation pathways is determined by the cumulative net CO2 emissions until the time of net zero CO2and the warming contribution of other GHGs and climate forcers at that time (high confidence). Cumulative net CO2 emissions from 2020 to the time of net zero CO2 are 510 (330–710) GtCO2 in pathways that limit warming to 1.5°C (>50%) with no or limited overshoot and 890 (640–1160) GtCO2 in pathways limiting warming to 2°C (>67%). These estimates are consistent with the assessment of remaining carbon budgets by WGI after adjusting for differences in peak warming levels. {3.3, Box 3.4}
Rapid reductions in non-CO2GHGs, particularly methane, would lower the level of peak warming (high confidence). Residual non-CO2 emissions at the time of reaching net zero CO2 range between 5 and 11 GtCO2-eq yr –1 in pathways limiting warming to 2°C (>67%) or lower. Methane (CH4) is reduced by around 19% (4–46%) in 2030 and 45% (29–64%) in 2050, relative to 2019. Methane emission reductions in pathways limiting warming to 1.5°C (>50%) with no or limited overshoot are substantially higher by 2030, 34% (21–57%), but only moderately so by 2050, 51% (35–70%). Methane emissions reductions are thus attainable at relatively lower GHG prices but are at the same time limited in scope in most 1.5°C–2°C pathways. Deeper methane emissions reductions by 2050 could further constrain the peak warming. N2O emissions are reduced too, but similar to CH4, emission reductions saturate for more stringent climate goals. In the mitigation pathways, the emissions of cooling aerosols are reduced due to reduced use of fossil fuels. The overall impact on non-CO2-related warming combines these factors. {3.3}
Net zero GHG emissions imply net negative CO2 emissions at a level compensating residual non-CO2 emissions. Only 30% of the pathways limiting warming to 2°C (>67%) or lower reach net zero GHG emissions in the 21st century (high confidence). In those pathways reaching net zero GHGs, it is achieved around 10 to 40 years later than for net zero CO2 (medium confidence). The reported quantity of residual non-CO2 emissions depends on accounting: the choice of GHG metric. Reaching and sustaining global net zero GHG emissions, measured in terms of GWP-100, results in a gradual decline of temperature ( high confidence). {Cross-Chapter Box 2 in Chapter 2, 3.3, Cross-Chapter Box 3 in this chapter}
Pathways limiting warming to 2°C (>67%) or lower exhibit substantial reductions in emissions from all sectors (high confidence). Projected CO2 emissions reductions between 2019 and 2050 in 1.5°C (>50%) pathways with no or limited overshoot are around 77% (31–96%) for energy demand, 115% (90–167%) for energy supply, and 148% (94–387%) for agriculture, forestry and other land use (AFOLU). In pathways limiting warming to 2°C (>67%), projected CO2 emissions are reduced between 2019 and 2050 by around 49% for energy demand, 97% for energy supply, and 136% for AFOLU (medium confidence). {3.4}
Delaying or sacrificing emissions reductions in one sector or region involves compensating reductions in other sectors or regions if warming is to be limited (high confidence). Mitigation pathways show differences in the timing of decarbonisation and when net zero CO2 emissions are achieved across sectors and regions. At the time of global net zero CO2 emissions, emissions in some sectors and regions are positive while others are negative; the ordering depends on the mitigation options available, the cost of those options, and the policies implemented. In cost-effective mitigation pathways, the energy-supply sector typically reaches net zero CO2 before the economy as a whole, while the demand sectors reach net zero CO2 later, if ever ( high confidence). {3.4}
Pathways limiting warming to 2°C (>67%) or lower involve substantial reductions in fossil fuel consumption and a near elimination of the use of coal without carbon capture and storage (CCS) (high confidence). These pathways show an increase in low-carbon energy, with 88% (69–97%) of primary energy coming from these sources by 2100. {3.4}
Stringent emissions reductions at the level required for 2°C (>67%) or lower are achieved through increased direct electrification of buildings, transport, and industry, resulting in increased electricity generation in all pathways (high confidence). Nearly all electricity in pathways limiting warming to 2°C (>67%) or lower is from low- or no-carbon technologies, with different shares of nuclear, biomass, non-biomass renewables, and fossil CCS across pathways. {3.4}
The measures required tolimit warming to 2°C (>67%) or lower can result in large-scale transformation of the land surface (high confidence). Pathways limiting warming to 2°C (>67%) or lower are projected to reach net zero CO2 emissions in the AFOLU sector between the 2020s and 2070, with an increase of forest cover of about 322 million ha (–67 to 890 million ha) in 2050 in pathways limiting warming to 1.5°C (>50%) with no or limited overshoot. Cropland area to supply biomass for bioenergy (including bioenergy with carbon capture and storage – BECCS) is around 199 (56–482) million ha in 2050 in pathways limiting warming to 1.5°C (>50%) with no or limited overshoot. The use of bioenergy can lead to either increased or reduced emissions, depending on the scale of deployment, conversion technology, fuel displaced, and how/where the biomass is produced ( high confidence). {3.4}
Anthropogenic land CO2 emissions and removals in Integrated Assessment Model (IAM) pathways cannot be directly compared with those reported in national GHG inventories (high confidence). Methodologies enabling a more like-for-like comparison between models’ and countries’ approaches would support more accurate assessment of the collective progress achieved under the Paris Agreement. {3.4, 7.2.2.5}
Pathways that limit warming to 2°C (>67%) or lowerinvolve some amount of CDR to compensate for residual GHG emissions remaining after substantial direct emissions reductions in all sectors and regions (high confidence). CDR deployment in pathways serves multiple purposes: accelerating the pace of emissions reductions, offsetting residual emissions, and creating the option for net negative CO2 emissions in case temperature reductions need to be achieved in the long term ( high confidence). CDR options in the pathways are mostly limited to BECCS, afforestation and direct air carbon capture and storage (DACCS). CDR through some measures in AFOLU can be maintained for decades but not in the very long term because these sinks will ultimately saturate ( high conf idence). {3.4}
Mitigation pathways show reductions in energy demand relative to reference scenarios, through a diverse set of demand-side interventions (high confidence). Bottom-up and non-IAM studies show significant potential for demand-side mitigation. A stronger emphasis on demand-side mitigation implies less dependence on CDR and, consequently, reduced pressure on land and biodiversity. {3.4, 3.7}
Limiting warming requires shifting energy investments away from fossilfuels and towards low-carbon technologies (high confidence). The bulk of investments are needed in medium- and low-income regions. Investment needs in the electricity sector are on average 2.3 trillion USD2015 yr –1 over 2023 to 2052 for pathways that limit warming to 1.5°C (>50%) with no or limited overshoot, and 1.7 trillion USD2015 yr –1 for pathways that limit warming to 2°C (>67%). {3.6.1}
Pathways limiting warming to 2°C (>67%) require more rapid near-term transformations and are associated with higher upfront transition costs, but meanwhile bring long-term gains for the economy as well as earlier benefits in avoided climate change impacts (high confidence). This conclusion is independent of the discount rate applied, though the modelled cost-optimal balance of mitigation action over time does depend on the discount rate. Lower discount rates favour earlier mitigation, reducing reliance on CDR and temperature overshoot. {3.6.1, 3.8}
Mitigation pathwaysthat limit warming to 2°C (>67%) entail losses in global GDP with respect to reference scenarios of between 1.3% and 2.7% in 2050; and in pathways that limit warming to 1.5°C (>50%) with no or limited overshoot, losses are between 2.6% and 4.2%. Yet, these estimates do not account for the economic benefits of avoided climate change impacts (medium confidence). In mitigation pathways that limit warming to 2°C (>67%), marginal abatement costs of carbon are about 90 (60–120) USD2015 tCO2 in 2030 and about 210 (140–340) USD2015 tCO2 in 2050; in pathways that limit warming to 1.5°C (>50%) with no or limited overshoot, they are about 220 (170–290) USD2015 tCO2 in 2030 and about 630 (430–990) USD2015 tCO2 in 2050. 3 {3.6.1}
The global benefits of pathways limiting warming to 2°C (>67%) outweigh global mitigation costs over the 21st century, if aggregated economic impacts of climate change are at the moderate to high end of the assessed range, and a weight consistent with economic theory is given to economic impacts over the longterm. This holds true even without accounting for benefits in other sustainable development dimensions or non-market damages from climate change (medium confidence). The aggregate global economic repercussions of mitigation pathways include the macroeconomic impacts of investments in low-carbon solutions and structural changes away from emitting activities, co-benefits and adverse side effects of mitigation, (avoided) climate change impacts, and (reduced) adaptation costs. Existing quantifications of global aggregate economic impacts show a strong dependence on socio-economic development conditions, as these shape exposure and vulnerability and adaptation opportunities and responses. (Avoided) impacts for poorer households and poorer countries represent a smaller share in aggregate economic quantifications expressed in GDP or monetary terms, whereas their well-being and welfare effects are comparatively larger. When aggregate economic benefits from avoided climate change impacts are accounted for, mitigation is a welfare-enhancing strategy ( high confidence). {3.6.2}
The economic benefits on human health from air quality improvement arising from mitigation action can be of the same order of magnitude as mitigation costs, and potentially even larger (medium confidence). {3.6.3}
Differences between aggregate employment in mitigation pathways compared to reference scenarios are relatively small, although there may be substantial reallocations across sectors, with job creation in some sectors and job losses in others (medium confidence). The net employment effect (and its sign) depends on scenario assumptions, modelling framework, and modelled policy design. Mitigation has implications for employment through multiple channels, each of which impacts geographies, sectors and skill categories differently (medium confidence). {3.6.4}
The economic repercussions of mitigation vary widely across regions and households, depending on policy design and level of international cooperation (high confidence). Delayed global cooperation increases policy costs across regions, especially in those that are relatively carbon intensive at present ( high confidence). Pathways with uniform carbon values show higher mitigation costs in more carbon-intensive regions, in fossil fuel exporting regions and in poorer regions ( high confidence). Aggregate quantifications expressed in GDP or monetary terms undervalue the economic effects on households in poorer countries; the actual effects on welfare and well-being are comparatively larger ( high confidence). Mitigation at the speed and scale required to limit warming to 2°C (>67%) or lower implies deep economic and structural changes, thereby raising multiple types of distributional concerns across regions, income classes and sectors ( high confidence). {3.6.1, 3.6.4}
The timing of mitigation actions and their effectiveness will have significant consequences for broader sustainable development outcomes in the longer term (high confidence). Ambitious mitigation can be considered a precondition for achieving the Sustainable Development Goals (SDGs), especially for vulnerable populations and ecosystems with little capacity to adapt to climate impacts. Dimensions with anticipated co-benefits include health, especially regarding air pollution, clean energy access and water availability. Dimensions with potential trade-offs include food, employment, water stress, and biodiversity, which come under pressure from large-scale CDR deployment, energy affordability/access, and mineral-resource extraction ( high confidence). {3.7}
Many of the potential trade-offs of mitigation measures for other sustainable development outcomes depend on policy design and can thus be compensated or avoided with additional policies and investments or through policies that integrate mitigation with other SDGs (high confidence). Targeted SDG policies and investments, for example in the areas of healthy nutrition, sustainable consumption and production, and international collaboration, can support climate change mitigation policies and resolve or alleviate trade-offs . Trade-offs can be addressed by complementary policies and investments, as well as through the design of cross-sectoral policies integrating mitigation with the Sustainable Development Goals of health, nutrition, sustainable consumption and production, equity and biodiversity. {3.7}
Decent living standards, which encompass many SDG dimensions, are achievable at lower energy use than previously thought (high confidence). Mitigation strategies that focus on lower demands for energy and land-based resources exhibit reduced trade-offs and negative consequences for sustainable development relative to pathways involving either high emissions and climate impacts or those with high consumption and emissions that are ultimately compensated by large quantities of BECCS. {3.7}
Different mitigation pathways are associated with different feasibility challenges, though appropriate enabling conditions can reduce these challenges (high confidence). Feasibility challenges are transient and concentrated in the next two to three decades ( high confidence). They are multidimensional, context-dependent and malleable to policy, technological and societal trends. {3.8}
Mitigation pathways are associated with significant institutional and economic feasibility challenges rather than technological and geophysical feasibility challenges (medium confidence). The rapid pace of technological development and deployment in mitigation pathways is not incompatible with historical records. Institutional capacity is rather a key limiting factor for a successful transition. Emerging economies appear to have the highest feasibility challenges in the short to medium term. {3.8}
Pathways relying on a broad portfolio of mitigation strategies are more robust and resilient (high confidence). Portfolios of technological solutions reduce the feasibility risks associated with the low-carbon transition. {3.8}"""
        ami_rake = AmiRake()
        ami_rake.read_text(text)
        scored_phrases = ami_rake.get_ranked_phrases_with_scores()
        print(scored_phrases[:20])
        assert len(scored_phrases) == 1237
        assert scored_phrases[:20] == [(58.877160104770205, '2 ° c (> 67 %) outweigh global mitigation costs'),
 (57.95613518374528, '2 ° c (> 67 %), marginal abatement costs'),
 (48.49721770370979, '2 ° c (> 67 %), projected co2 emissions'),
 (47.3922902494331, 'net ghg emissions typically around 21 – 36 gtco2'),
 (47.262441490051586, '2 ° c (> 67 %) entail losses'),
 (47.25053672814683, '2 ° c (> 67 %) reach 50'),
 (44.38198388050872, 'net zero ghg emissions imply net negative co2 emissions'),
 (42.59577482338492, '2 ° c (> 67 %) converge'),
 (40.59577482338492, '2 ° c (> 67 %) require'),
 (40.17258297258297, 'around 480 – 750 ej yr – 1'),
 (39.70265143345301, '5 ° c – 2 ° c pathways'),
 (39.61047619047619,
  'effective mitigation pathways assuming immediate action1 tolimit warming'),
 (37.45599715918865, '5 ° c (> 50 %) pathways'),
 (35.74184782608695, 'supply sector typically reaches net zero co2'),
 (35.59577482338492, '2 ° c (> 67 %)'),
 (35.59577482338492, '2 ° c (> 67 %)'),
 (35.59577482338492, '2 ° c (> 67 %)'),
 (35.59577482338492, '2 ° c (> 67 %)'),
 (35.59577482338492, '2 ° c (> 67 %)'),
 (35.59577482338492, '2 ° c (> 67 %)')]


    def test_bloom2_filter(self):
        """
        quick index with adjustable error rate
        """
        from bloom_filter2 import BloomFilter

        # instantiate BloomFilter with custom settings,
        # max_elements is how many elements you expect the filter to hold.
        # error_rate defines accuracy; You can use defaults with
        # `BloomFilter()` without any arguments. Following example
        # is same as defaults:
        bloom = BloomFilter(max_elements=10000, error_rate=0.1)

        # Test whether the bloom-filter has seen a key:
        assert "test-key" not in bloom

        # Mark the key as seen
        bloom.add("test-key")

    @unittest.skip("cannot load/run ImportError: numpy.core.multiarray failed to import")
    def test_pke(self):
        """
        tests PKE - python keyphrase extraction
        https://github.com/boudinfl/pke?tab=readme-ov-file#minimal-example
        """
        import pke

        # initialize keyphrase extraction model, here TopicRank
        extractor = pke.unsupervised.TopicRank()

        # load the content of the document, here document is expected to be a simple
        # test string and preprocessing is carried out using spacy
        extractor.load_document(input='text', language='en')

        # keyphrase candidate selection, in the case of TopicRank: sequences of nouns
        # and adjectives (i.e. `(Noun|Adj)*`)
        extractor.candidate_selection()

        # candidate weighting, in the case of TopicRank: using a random walk algorithm
        extractor.candidate_weighting()

        # N-best selection, keyphrases contains the 10 highest scored candidates as
        # (keyphrase, score) tuples
        keyphrases = extractor.get_n_best(n=10)


