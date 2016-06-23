from opengever.base.transforms import trix2sablon
from opengever.testing import FunctionalTestCase
import string


TRIX_MARKUP = u"""
<div>
  Lorem ipsum dolor sit amet, consectetur adipiscing elit. Huius,
  Lyco, oratione locuples, rebus ipsis ielunior. Duo enim genera quae erant,
  fecit tria. Hoc loco discipulos quaerere videtur, ut, qui asoti esse velint,
  philosophi ante fiant. Sed quanta sit alias, nunc tantum possitne esse
  tanta. Duo Reges: constructio interrete. Non enim ipsa genuit hominem, sed
  accepit a natura inchoatum. Nunc ita separantur, ut disiuncta sint, quo
  nihil potest esse perversius.<br>
  Hoc tu nunc in illo probas.<br>
  <br>
</div>
<ol>
  <li>
    Num igitur utiliorem tibi hunc <strong>Triarium putas
    esse</strong> posse, quam si tua sint Puteolis granaria?
  </li>
  <li>
    Sin autem est in ea, quod quidam volunt, nihil impedit hanc
    nostram comprehensionem summi boni.
  </li>
  <li>
    Quid affers, cur Thorius, cur <em>Caius Postumius</em>, cur
    omnium horum magister, Orata, non iucundissime vixerit?
  </li>
</ol>
<div>
  <br>
</div>
<div>

  Quodsi ipsam honestatem undique pert<em>ectam atque absolutam. No</em>n
  quaeritur autem quid naturae tuae consentaneum sit, sed quid disciplinae.
  Polycratem Samium felicem appellabant. In eo enim positum est id, quod
  dicimus esse expetendum.&nbsp;<br>
  <br>
</div>
<ul>
  <li>
    Minime id quidem, inquam, alienum, multumque ad ea, quae q
    uaerimus, explicatio tua ista profecerit.
  </li>
  <li>
    Itaque his sapiens semper vacabit.
  </li>
  <li>
    Atque ab his initiis profecti <strong>omnium virtutum et
    origin</strong>em et progressionem persecuti sunt.
  </li>
  <li>

    Expressa vero in iis aetatibus, quae iam confirmatae sunt.
  </li>
  <li>

    Maximas vero virtutes iacere omnis necesse est voluptate dominante.
  </li>
</ul>
<div>
  <br>
</div>
<div>
  Illum mallem <strong>levares, quo optimum atque huma</strong>
  nissimum virum, Cn. Tu quidem reddes; Deprehensus omnem poenam contemnet.
  Non quaeritur autem quid naturae tuae consentaneum sit, sed quid
  disciplinae.&nbsp;
</div>
<div>
  Ita graviter et severe voluptatem secrevit a bono. Ergo ita:
  non posse honeste vivi, nisi honeste vivatur? Quamvis enim depravatae non
  sint, pravae tamen esse possunt. Ita enim vivunt quidam, ut eorum vita
  refellatur oratio. Ex quo illud efficitur, qui bene cenent omnis libenter
  cenare, qui libenter, non continuo bene. Sed in rebus apertissimis nimium
  longi sumus. Cur igitur, cum de re conveniat, non malumus usitate loqui?
  Quae hic rei publicae vulnera inponebat, eadem ille sanabat.&nbsp;
</div>
<div>
  Rhetorice igitur, inquam, nos mavis quam dialectice disputare?
  Quod, inquit, quamquam voluptatibus quibusdam est saepe i ucundius, tamen
  expetitur propter voluptatem. Sed quae tandem ista ratio est? Cum id
  fugiunt, re eadem defendunt, quae Peripatetici, verba. Sic enim censent,
  oportunitatis esse beate vivere. Expectoque quid ad id, quod quaerebam,
  respondeas. At cum de plurimis eadem dicit, tum certe de maximis. Is ita
  vivebat, ut nulla tam exquisita posset inveniri voluptas, qua non
  abundaret. Non enim, si omnia non sequebatur, idcirco non erat ortus illinc.
</div>
"""


class TestTrixSablonTransform(FunctionalTestCase):

    maxDiff = None

    def apply_transform(self, value):
        return trix2sablon.convert(value)

    def test_transform_strips_disallowed_html_tags(self):
        value = (
            "<div><span>Foo</span><abbr>gnahahah</abbr>"
            "<h1>Title</h1>"
            "</div>"
        )
        self.assertEqual(
            "<div>FoognahahahTitle</div>", self.apply_transform(value))

    def test_transform_doesnt_strip_whitespace_when_all_elements_are_valid(self):
        value = """&nbsp;
            <div>
        </div>
        """ + string.whitespace

        self.assertEqual(value, self.apply_transform(value))

    def test_transform_doesnt_strip_whitespace_when_stripping_invalid_tags(self):
        value = "\n<span>\n\n\t  Foo!  </span>"

        self.assertEqual("\n\n\n\t  Foo!  ", self.apply_transform(value))

    def test_transform_rewrites_self_closing_br_tag(self):
        self.assertEqual("<br>", self.apply_transform("<br />"))
        self.assertEqual("<br>", self.apply_transform("<br  />"))

    def test_transform_keeps_br_tag(self):
        self.assertEqual("<br>", self.apply_transform("<br>"))

    def test_trix_markup_is_left_unchanged(self):
        self.assertEqual(TRIX_MARKUP, self.apply_transform(TRIX_MARKUP))
