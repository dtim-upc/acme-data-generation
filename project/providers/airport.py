import typing as T
from collections import OrderedDict
from datetime import datetime, timedelta
import random
from string import ascii_letters, digits, punctuation, ascii_uppercase
import math

from faker import Faker
from faker.providers import BaseProvider

from project.models.declarative import aims, amos
from project.models.data.serializable import Manufacturer, Reporter


class AirportProvider(BaseProvider):
    def random_string(
        self,
        str_size: int = 5,
        allowed_chars: str = ascii_letters + punctuation + digits,
    ):
        # https://www.askpython.com/python/examples/generate-random-strings-in-python
        return "".join(
            random.SystemRandom().choice(allowed_chars) for _ in range(str_size)
        )

    def make_noisy(
        self, string: str, alter_case: bool = True, max_whitespace: int = 0
    ) -> str:
        """Introduces noise in strings at random

        It alters the case of strings at random, and introduces trailing whitespace

        >>> make_noisy("acme")
        '   ACmE'

        >>> make_noisy("acme")
        '     Acme'

        """

        altered_case = (
            (
                char.upper() if self.generator.pybool() else char.lower()
                for char in string
            )
            if alter_case
            else string
        )

        leading_whitespace = " " * self.random_int(0, max_whitespace)
        trailing_whitespace = " " * self.random_int(0, max_whitespace)

        return leading_whitespace + "".join(altered_case) + trailing_whitespace

    _airport_codes: T.List[str] = [
        "TIA",
        "EVN",
        "GRZ",
        "INN",
        "KLU",
        "LNZ",
        "SZG",
        "VIE",
        "GYD",
        "MSQ",
        "ANR",
        "BRU",
        "CRL",
        "LGG",
        "OST",
        "SJJ",
        "TZL",
        "BOJ",
        "SOF",
        "VAR",
        "DBV",
        "PUY",
        "SPU",
        "ZAD",
        "ZAG",
        "LCA",
        "PFO",
        "BRQ",
        "PRG",
        "AAL",
        "AAR",
        "BLL",
        "CPH",
        "FAE",
        "TLL",
        "HEL",
        "OUL",
        "RVN",
        "TMP",
        "TKU",
        "VAA",
        "AJA",
        "BIA",
        "EGC",
        "BIQ",
        "BOD",
        "BES",
        "FSC",
        "LIL",
        "LYS",
        "MRS",
        "MPL",
        "NTE",
        "NCE",
        "BVA",
        "CDG",
        "ORY",
        "SXB",
        "RNS",
        "RUN",
        "TLN",
        "TLS",
        "TBS",
        "FMM",
        "BER",
        "SXF",
        "TXL",
        "BRE",
        "CGN",
        "DTM",
        "DRS",
        "DUS",
        "FRA",
        "HHN",
        "FDH",
        "HAM",
        "HAJ",
        "FKB",
        "LEJ",
        "MUC",
        "FMO",
        "NUE",
        "PAD",
        "STR",
        "NRN",
        "ATH",
        "CHQ",
        "CFU",
        "HER",
        "KGS",
        "JMK",
        "RHO",
        "JTR",
        "SKG",
        "ZTH",
        "BUD",
        "DEB",
        "KEF",
        "ORK",
        "DUB",
        "NOC",
        "KIR",
        "SNN",
        "AHO",
        "AOI",
        "BRI",
        "BGY",
        "BLQ",
        "BDS",
        "CAG",
        "CTA",
        "CIY",
        "FLR",
        "GOA",
        "SUF",
        "LIN",
        "MXP",
        "NAP",
        "OLB",
        "PMO",
        "PEG",
        "PSR",
        "PSA",
        "CIA",
        "FCO",
        "TPS",
        "TSF",
        "TRN",
        "VCE",
        "VRN",
        "ALA",
        "TSE",
        "PRN",
        "RIX",
        "KUN",
        "VNO",
        "LUX",
        "SKP",
        "MLA",
        "KIV",
        "TGD",
        "TIV",
        "AMS",
        "EIN",
        "GRQ",
        "MST",
        "RTM",
        "AES",
        "BGO",
        "BOO",
        "HAU",
        "KRS",
        "OSL",
        "TRF",
        "SVG",
        "TOS",
        "TRD",
        "GDN",
        "KTW",
        "KRK",
        "POZ",
        "WAW",
        "WMI",
        "WRO",
        "FAO",
        "LIS",
        "FNC",
        "PDL",
        "OPO",
        "OTP",
        "CLJ",
        "IAS",
        "TSR",
        "SVX",
        "DME",
        "SVO",
        "VKO",
        "OVB",
        "LED",
        "AER",
        "BEG",
        "INI",
        "BTS",
        "KSC",
        "LJU",
        "ALC",
        "LEI",
        "OVD",
        "BCN",
        "BIO",
        "FUE",
        "GRO",
        "LPA",
        "IBZ",
        "XRY",
        "SPC",
        "ACE",
        "MAD",
        "AGP",
        "MAH",
        "PMI",
        "RMU",
        "REU",
        "SDR",
        "SCQ",
        "SVQ",
        "TFN",
        "TFS",
        "VLC",
        "ZAZ",
        "GOT",
        "MMX",
        "ARN",
        "BMA",
        "NYO",
        "VST",
        "BSL",
        "BRN",
        "GVA",
        "LUG",
        "ZRH",
        "ADA",
        "ESB",
        "AYT",
        "DLM",
        "IST",
        "SAW",
        "ADB",
        "BJV",
        "TZX",
        "KBP",
        "IEV",
        "LWO",
        "ODS",
        "ABZ",
        "BHD",
        "BFS",
        "BHX",
        "BRS",
        "CWL",
        "DSA",
        "EMA",
        "EDI",
        "EXT",
        "GLA",
        "PIK",
        "HUY",
        "JER",
        "LBA",
        "LPL",
        "LCY",
        "LGW",
        "LHR",
        "LTN",
        "SEN",
        "STN",
        "MAN",
        "NCL",
        "SOU",
    ]

    _register_prefix: str = "XY-"
    _alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    _digits: str = "0123456789"

    _offset_timestamp: datetime = datetime.strptime(
        "2010-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
    )

    _end_timestamp: datetime = datetime.strptime(
        "2017-01-07 00:00:00", "%Y-%m-%d %H:%M:%S"
    )

    _delay_codes: T.List[str] = [
        "00",
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "31",
        "32",
        "33",
        "34",
        "35",
        "36",
        "37",
        "38",
        "39",
        "41",
        "42",
        "43",
        "44",
        "45",
        "46",
        "47",
        "48",
        "51",
        "52",
        "55",
        "56",
        "57",
        "58",
        "61",
        "62",
        "63",
        "64",
        "65",
        "66",
        "67",
        "68",
        "69",
        "71",
        "72",
        "73",
        "75",
        "76",
        "77",
        "81",
        "82",
        "83",
        "84",
        "85",
        "86",
        "87",
        "88",
        "89",
        "91",
        "92",
        "93",
        "94",
        "95",
        "96",
        "97",
        "98",
        "99",
    ]

    _slot_kinds: T.List[str] = ["Flight", "Maintenance"]

    _maintenance_event_kinds_flight_slot: T.List[str] = [
        "Delay",
        "Safety",
    ]

    _maintenance_event_kinds_maintenance_slot: T.List[str] = [
        "AircraftOnGround",
        "Maintenance",
        "Revision",
    ]

    _ata_codes: T.List[str] = [
        "1100",
        "1210",
        "1220",
        "1230",
        "1240",
        "1400",
        "1410",
        "1420",
        "1430",
        "1497",
        "1800",
        "1810",
        "1820",
        "1897",
        "2100",
        "2110",
        "2120",
        "2121",
        "2130",
        "2131",
        "2132",
        "2133",
        "2134",
        "2140",
        "2150",
        "2160",
        "2161",
        "2162",
        "2163",
        "2170",
        "2197",
        "2200",
        "2210",
        "2211",
        "2212",
        "2213",
        "2214",
        "2215",
        "2216",
        "2220",
        "2230",
        "2250",
        "2297",
        "2300",
        "2310",
        "2311",
        "2312",
        "2320",
        "2330",
        "2340",
        "2350",
        "2360",
        "2370",
        "2397",
        "2400",
        "2410",
        "2420",
        "2421",
        "2422",
        "2423",
        "2424",
        "2425",
        "2430",
        "2431",
        "2432",
        "2433",
        "2434",
        "2435",
        "2436",
        "2437",
        "2440",
        "2450",
        "2460",
        "2497",
        "2500",
        "2510",
        "2520",
        "2530",
        "2540",
        "2550",
        "2551",
        "2560",
        "2561",
        "2562",
        "2563",
        "2564",
        "2565",
        "2570",
        "2571",
        "2572",
        "2597",
        "2600",
        "2610",
        "2611",
        "2612",
        "2613",
        "2620",
        "2621",
        "2622",
        "2697",
        "2700",
        "2701",
        "2710",
        "2711",
        "2720",
        "2721",
        "2722",
        "2730",
        "2731",
        "2740",
        "2741",
        "2742",
        "2750",
        "2751",
        "2752",
        "2760",
        "2761",
        "2770",
        "2780",
        "2781",
        "2782",
        "2797",
        "2800",
        "2810",
        "2820",
        "2821",
        "2822",
        "2823",
        "2824",
        "2830",
        "2840",
        "2841",
        "2842",
        "2843",
        "2844",
        "2897",
        "2900",
        "2910",
        "2911",
        "2912",
        "2913",
        "2914",
        "2915",
        "2916",
        "2917",
        "2920",
        "2921",
        "2922",
        "2923",
        "2925",
        "2926",
        "2927",
        "2930",
        "2931",
        "2932",
        "2933",
        "2934",
        "2997",
        "3000",
        "3010",
        "3020",
        "3030",
        "3040",
        "3050",
        "3060",
        "3070",
        "3080",
        "3097",
        "3100",
        "3110",
        "3120",
        "3130",
        "3140",
        "3150",
        "3160",
        "3170",
        "3197",
        "3200",
        "3201",
        "3210",
        "3211",
        "3212",
        "3213",
        "3220",
        "3221",
        "3222",
        "3230",
        "3231",
        "3232",
        "3233",
        "3234",
        "3240",
        "3241",
        "3242",
        "3243",
        "3244",
        "3245",
        "3246",
        "3250",
        "3251",
        "3252",
        "3260",
        "3270",
        "3297",
        "3300",
        "3310",
        "3320",
        "3330",
        "3340",
        "3350",
        "3397",
        "3400",
        "3410",
        "3411",
        "3412",
        "3413",
        "3414",
        "3415",
        "3416",
        "3417",
        "3418",
        "3420",
        "3421",
        "3422",
        "3423",
        "3424",
        "3425",
        "3430",
        "3431",
        "3432",
        "3433",
        "3434",
        "3435",
        "3436",
        "3440",
        "3441",
        "3442",
        "3443",
        "3444",
        "3445",
        "3446",
        "3450",
        "3451",
        "3452",
        "3453",
        "3454",
        "3455",
        "3456",
        "3457",
        "3460",
        "3461",
        "3497",
        "3500",
        "3510",
        "3520",
        "3530",
        "3597",
        "3600",
        "3610",
        "3620",
        "3697",
        "3700",
        "3710",
        "3720",
        "3797",
        "3800",
        "3810",
        "3820",
        "3830",
        "3840",
        "3897",
        "4500",
        "4597",
        "4900",
        "4910",
        "4920",
        "4930",
        "4940",
        "4950",
        "4960",
        "4970",
        "4980",
        "4990",
        "4997",
        "5100",
        "5101",
        "5102",
        "5200",
        "5210",
        "5220",
        "5230",
        "5240",
        "5241",
        "5242",
        "5243",
        "5244",
        "5245",
        "5246",
        "5247",
        "5248",
        "5250",
        "5260",
        "5270",
        "5280",
        "5297",
        "5300",
        "5301",
        "5302",
        "5310",
        "5311",
        "5312",
        "5313",
        "5314",
        "5315",
        "5320",
        "5321",
        "5322",
        "5323",
        "5324",
        "5330",
        "5340",
        "5341",
        "5342",
        "5343",
        "5344",
        "5345",
        "5346",
        "5347",
        "5350",
        "5397",
        "5400",
        "5410",
        "5411",
        "5412",
        "5413",
        "5414",
        "5415",
        "5420",
        "5497",
        "5500",
        "5510",
        "5511",
        "5512",
        "5513",
        "5514",
        "5520",
        "5521",
        "5522",
        "5523",
        "5524",
        "5530",
        "5531",
        "5532",
        "5533",
        "5534",
        "5540",
        "5541",
        "5542",
        "5543",
        "5544",
        "5550",
        "5551",
        "5552",
        "5553",
        "5554",
        "5597",
        "5600",
        "5610",
        "5620",
        "5630",
        "5640",
        "5697",
        "5700",
        "5710",
        "5711",
        "5712",
        "5713",
        "5714",
        "5720",
        "5730",
        "5740",
        "5741",
        "5742",
        "5743",
        "5744",
        "5750",
        "5751",
        "5752",
        "5753",
        "5754",
        "5755",
        "5797",
        "6100",
        "6110",
        "6111",
        "6112",
        "6113",
        "6114",
        "6120",
        "6121",
        "6122",
        "6123",
        "6130",
        "6140",
        "6197",
        "6200",
        "6210",
        "6220",
        "6230",
        "6240",
        "6297",
        "6300",
        "6310",
        "6320",
        "6321",
        "6322",
        "6330",
        "6340",
        "6397",
        "6400",
        "6410",
        "6420",
        "6440",
        "6497",
        "6500",
        "6510",
        "6520",
        "6540",
        "6597",
        "6700",
        "6710",
        "6711",
        "6720",
        "6730",
        "6797",
        "7100",
        "7110",
        "7111",
        "7112",
        "7120",
        "7130",
        "7160",
        "7170",
        "7197",
        "7200",
        "7210",
        "7220",
        "7230",
        "7240",
        "7250",
        "7260",
        "7261",
        "7270",
        "7297",
        "7300",
        "7310",
        "7311",
        "7312",
        "7313",
        "7314",
        "7320",
        "7321",
        "7322",
        "7323",
        "7324",
        "7330",
        "7331",
        "7332",
        "7333",
        "7334",
        "7397",
        "7400",
        "7410",
        "7411",
        "7412",
        "7413",
        "7414",
        "7420",
        "7421",
        "7430",
        "7497",
        "7500",
        "7510",
        "7520",
        "7530",
        "7531",
        "7532",
        "7540",
        "7597",
        "7600",
        "7601",
        "7602",
        "7603",
        "7620",
        "7697",
        "7700",
        "7710",
        "7711",
        "7712",
        "7713",
        "7714",
        "7720",
        "7721",
        "7722",
        "7730",
        "7731",
        "7732",
        "7740",
        "7797",
        "7800",
        "7810",
        "7820",
        "7830",
        "7897",
        "7900",
        "7910",
        "7920",
        "7921",
        "7922",
        "7923",
        "7930",
        "7931",
        "7932",
        "7933",
        "7997",
        "8000",
        "8010",
        "8011",
        "8012",
        "8097",
        "8100",
        "8110",
        "8120",
        "8197",
        "8200",
        "8297",
        "8300",
        "8397",
        "8500",
        "8510",
        "8520",
        "8530",
        "8540",
        "8550",
        "8560",
        "8570",
        "8597",
    ]

    _work_order_kinds: T.List[str] = ["Forecast", "TechnicalLogBook"]
    _frequency_units_kinds: T.List[str] = ["Flights", "Days", "Miles"]
    _mel_category_kinds: T.List[str] = ["A", "B", "C", "D"]
    _report_kinds: T.List[str] = ["PIREP", "MAREP"]
    _aircraft_models: T.List[str] = [
        "A319",
        "A320 family",
        "A320neo family",
        "A321",
        "A330",
        "A330neo",
        "A340",
        "A350 XWB",
        "737",
        "747",
        "767",
        "777",
    ]

    _aircraft_manufacturers: T.List[str] = [
        "Airbus",
        "Boeing",
    ]

    def _quality_dispatcher(self, mapping, quality):
        """Used to dispatch a value in function of the quality"""
        if quality not in ("good", "bad", "noisy"):
            raise ValueError('quality must be either "good", "bad" or "noisy"')

        if mapping.get("noisy") is None:
            mapping["noisy"] = self.make_noisy(mapping["good"])

        return mapping[quality]

    def quality(self, weights=None):
        """Returns a random quality value"""
        choices = ["good", "noisy", "bad"]
        return random.choices(choices, weights=weights, k=1)[0]

    def airport_code(self, quality: str = "good") -> str:
        mapping = {
            "bad": self.bothify("#??"),  # e.g. 3Ws, 1fR
            "good": self.random_element(self._airport_codes),
        }

        return self._quality_dispatcher(mapping, quality)

    def delay_code(self, quality: str = "good") -> str:
        mapping = {
            "bad": self.bothify("##"),  # e.g. 123, 999
            "good": self.random_element(self._delay_codes),
        }

        return self._quality_dispatcher(mapping, quality)

    def slot_kind(self, quality: str = "good") -> str:
        mapping = {
            # "bad": self.bothify("###"),  # e.g. 123, 999 # deprecated, see issue #2
            "good": self.random_element(self._slot_kinds),
        }

        mapping["bad"] = mapping["noisy"] = mapping["good"]

        return self._quality_dispatcher(mapping, quality)

    def maintenance_event_kind(self, quality: str = "good", kind: T.Optional[str] = None) -> str:
        """return a maintenanceeventkind for any slot"""

        if kind == "Flight":
            provider = self._maintenance_event_kinds_flight_slot
        elif kind == "Maintenance":
            provider = self._maintenance_event_kinds_maintenance_slot
        else:
            provider = self._maintenance_event_kinds_maintenance_slot + self._maintenance_event_kinds_flight_slot

        mapping = {
            "good": self.random_element(provider)
        }

        # maintenanceevent kind is a datatype and raises issues if not right
        mapping["bad"] = mapping["noisy"] = mapping["good"]

        return self._quality_dispatcher(mapping, quality)

    def ata_code(self, quality: str = "good") -> str:
        mapping = {
            "good": self.random_element(self._ata_codes),
            "bad": self.random_string(4),
        }
        return self._quality_dispatcher(mapping, quality)

    def work_order_kind(self, quality: str = "good") -> str:
        mapping = {
            "good": self.random_element(self._work_order_kinds),
            # "bad": self.random_string(random.randint(5, 10)),
        }

        mapping["bad"] = mapping["noisy"] = mapping["good"]

        return self._quality_dispatcher(mapping, quality)

    def frequency_units_kind(self, quality: str = "good") -> str:
        mapping = {
            "good": self.random_element(self._frequency_units_kinds),
            # "bad": self.random_string(random.randint(2, 5)),
        }

        mapping["bad"] = mapping["noisy"] = mapping["good"]
        return self._quality_dispatcher(mapping, quality)

    def mel_category_kind(self, quality: str = "good") -> str:
        mapping = {
            "good": self.random_element(self._mel_category_kinds),
            # "bad": self.random_string(random.randint(5, 10)),
        }

        mapping["bad"] = mapping["noisy"] = mapping["good"]

        return self._quality_dispatcher(mapping, quality)

    def report_kind(self, quality: str = "good") -> str:
        mapping = {
            "good": self.random_element(self._report_kinds),
            # "bad": self.random_string(5, ascii_uppercase),
        }

        mapping["bad"] = mapping["noisy"] = mapping["good"]

        return self._quality_dispatcher(mapping, quality)

    def aircraft_model(self, quality: str = "good") -> str:
        mapping = {
            "good": self.random_element(self._aircraft_models),
            "bad": self.random_string(random.randint(5, 14)),
        }
        return self._quality_dispatcher(mapping, quality)

    def aircraft_manufacturer(self, quality: str = "good") -> str:
        mapping = {
            "good": self.random_element(self._aircraft_manufacturers),
            "bad": self.generator.company()
            }
        return self._quality_dispatcher(mapping, quality)

    def flight_route(self) -> T.List[str]:
        return self.random_elements(self._airport_codes, unique=True, length=2)

    def flight_number(self, quality="good") -> str:
        """Returns a random flight number between 1000 and 9999

        Returns:
            str: flight number, as a string
        """
        mapping = {
            "good": self.numerify("%%%%"),
            "bad": self.random_string(4, digits + ascii_letters),
        }
        return self._quality_dispatcher(mapping, quality)

    def flight_timestamp(self, quality="good") -> datetime:
        """produces random timestamp between two dates

        Note: these dates are hardcoded in the provider.

        Returns:
            datetime: a random datetime object
        """
        mapping = {
            "good": self.generator.date_time_between_dates(
                self._offset_timestamp, self._end_timestamp
            ),
        }

        # we add or substract 50-500 years at random
        random_timedelta = self.random_element([-1, 1]) * timedelta(
            days=random.randint(50 * 365, 100 * 365)
        )
        mapping["bad"] = mapping["good"] + random_timedelta

        # TODO: implement this. can't think of anything now
        mapping["noisy"] = mapping["good"]

        return self._quality_dispatcher(mapping, quality)

    def aircraft_registration_code(
        self, prefix: str = None, quality: str = "good"
    ) -> str:
        register_prefix: str = prefix or self._register_prefix

        mapping = {
            "good": register_prefix + self.lexify(text=f"???", letters=self._alphabet),
            "bad": self.random_string(6, digits + ascii_letters),
        }

        return self._quality_dispatcher(mapping, quality)

    def fleet(self, fleet_size: int, quality: str = "good") -> T.List[str]:
        return [
            self.aircraft_registration_code(quality=quality) for _ in range(fleet_size)
        ]

    def manufacturer_serial_number(self, quality="good") -> str:

        mapping = {
            "good": self.numerify(text="MSN %%%%"),
            "bad": self.random_string(random.randint(2, 3), ascii_uppercase)
            + " "
            + self.random_string(random.randint(3, 6), digits + punctuation),
        }

        return self._quality_dispatcher(mapping, quality)

    def maintenance_id(self, max_id: int = 999, quality="good") -> str:
        # R3
        mid = "_".join(
            [
                str(self.random_int(max=max_id)),
                str(
                    self.flight_timestamp(quality=quality)
                    + self.interruption_duration(quality=quality)
                ),
            ]
        )

        mapping = {
            "good": mid,
            "bad": self.random_string(6, digits + ascii_letters),
        }

        return self._quality_dispatcher(mapping, quality)

    def duration(
        self, max_days: int = 0, max_hours: int = 0, max_minutes: int = 0
    ) -> timedelta:

        return timedelta(
            days=self.random_int(max=max_days),
            hours=self.random_int(max=max_hours),
            minutes=self.random_int(max=max_minutes),
        )

    def interruption_duration(
        self,
        interruption_type: T.Optional[str] = None,
        return_type: bool = False,
        quality="good",
    ) -> T.Union[timedelta, T.Tuple[str, timedelta]]:
        """Returns a time interval specific to some interruption type.

        If no interruption type is provided, then an interruption type is
        generated internally.

        :return: A duration object or a tuple with the type and duration
        :rtype: T.Union[timedelta, T.Tuple[str, timedelta]]
        """
        if interruption_type is None:
            interruption_type = self.maintenance_event_kind(quality=quality)

        # setup depending on the maintenance kind obtained
        # R15
        if interruption_type == "Delay":
            duration = self.duration(max_minutes=59)
        elif interruption_type == "Safety":
            # these values were taken from the Java code sample from petar
            duration = self.duration(max_days=89, max_hours=23, max_minutes=59)
        elif interruption_type == "AircraftOnGround":
            duration = self.duration(max_hours=23, max_minutes=59)
        elif interruption_type == "Maintenance":
            duration = self.duration(max_days=1, max_hours=23, max_minutes=59)
            # TODO: this is rule R15-D
            if duration > timedelta(days=1):
                duration = timedelta(days=1)
        elif interruption_type == "Revision":
            # days to one month (31 days)
            duration = self.duration(max_days=31, max_hours=0, max_minutes=0)
        else:
            # empty timedelta
            duration = timedelta()

        if quality == "bad":
            duration = duration * self.random_int(-100, 100)

        if return_type:
            return (interruption_type, duration)

        return duration

    def mel_reporting_deadline_duration(
        self, mel_type: T.Optional[str] = None,
        quality: str = "good"
        ) -> timedelta:
        """Returns a timedelta duration object, based on a MEL type.
        """

        if quality == "bad":
            mel_type = "bad"

        if mel_type is None:
            mel_type = self.mel_category_kind()

        _mel_mapping = {
            "A": timedelta(days=3),
            "B": timedelta(days=10),
            "C": timedelta(days=30),
            "D": timedelta(days=120),
            "bad": timedelta(days=self.random_int(max=500))
        }

        return _mel_mapping.get(mel_type, timedelta())

    # ---------------------------------------------------------------------------- #
    #                          beginning of random objects                         #
    # ---------------------------------------------------------------------------- #

    # ---------------------------------------------------------------------------- #
    #   Entities that are not stored in a table                                    #
    # ---------------------------------------------------------------------------- #

    def manufacturer(self, quality="good") -> Manufacturer:
        """Returns a random instance of Manufacturer

        Returns:
            Manufacturer: A random instance of Manufacturer
        """
        return Manufacturer(
            aircraft_reg_code=self.aircraft_registration_code(quality=quality),
            manufacturer_serial_number=self.manufacturer_serial_number(quality=quality),
            aircraft_model=self.aircraft_model(quality=quality),
            aircraft_manufacturer=self.aircraft_manufacturer(quality=quality),
        )

    def reporter(self, quality="good") -> Reporter:
        """Returns an instance of a Reporter with random attributes

        :return: a Reporter instance
        :rtype: Reporter
        """

        return Reporter(
            reporteurid=self.random_int(), airport=self.airport_code(quality=quality)
        )

    # ---------------------------------------------------------------------------- #
    #                                     AMOS                                     #
    # ---------------------------------------------------------------------------- #

    def work_package(
        self,
        max_id: int = 9999,
        quality: str = "good",
        work_order: T.Optional[
            T.Union[
                amos.TechnicalLogbookOrder, 
                amos.ForecastedOrder, 
                amos.WorkOrder]] = None,
    ) -> amos.Workpackage:
        """Produces a random workpackage object, possibly seeded

        :param quality: the quality of the random object generated, defaults to "good"
        :param maintenance_event: If provided, executiondate and executionplace are obtained from this object, defaults to None
        """

        workpackageid = getattr(work_order, "workpackage", self.random_int(max=max_id))

        executiondate = getattr(
            work_order, "executiondate", self.flight_timestamp(quality=quality)
        )

        executionplace = getattr(
            work_order, "executionplace", self.airport_code(quality=quality)
        )

        return amos.Workpackage(
            workpackageid=workpackageid,
            executiondate=executiondate,
            executionplace=executionplace,
        )

    def attachment(
        self, 
        operational_interruption: T.Optional[amos.OperationalInterruption] = None,
        quality = "good"
    ) -> amos.Attachment:

        oi = (operational_interruption or 
                self.operational_interruption_event(quality=quality))

        return amos.Attachment(
            file=self.generator.uuid4(), event=oi.maintenanceid
        )  # R4  # R5

    def work_order(
        self,
        max_id: int = 9999,
        quality: str = "good",
        maintenance_event: T.Optional[amos.MaintenanceEvent] = None,
        work_package: T.Optional[amos.Workpackage] = None,
        kind: T.Optional[str] = None
        ) -> T.Union[amos.WorkOrder, amos.ForecastedOrder, amos.TechnicalLogbookOrder]:

        """Produces a random instance of a work order object, based on `kind`

        If `kind` is `None`, then it produces a random instance of `amos.WorkOrder`
        """

        # early arg validation
        if kind:
            (assert (kind in {"Forecast", "TechnicalLogBook"}),
                'kind must be one of {"Forecast", "TechnicalLogBook"}')
        
        # a work order is referenced from at least one maintenance event
        maintenance_event = maintenance_event or self.maintenance_event(quality=quality)
        # a work order produces at least one work package
        work_package = work_package or self.work_package(quality=quality)
        
        # R25-A
        aircraft_registration = maintenance_event.aircraftregistration

        # R25-B
        executiondate = self.generator.date_time_ad(
            start_datetime=maintenance_event.starttime,
            end_datetime=maintenance_event.starttime + maintenance_event.duration,
        )

        # R25-C
        executionplace = maintenance_event.airport
        
        # other random attributes
        workorderid = self.random_int(max=max_id)
        workpackageid = work_package.workpackageid

        if kind == "Forecast":

            # R26
            deadline = self.generator.date_time_ad(
                start_datetime=executiondate,
                end_datetime=maintenance_event.starttime + maintenance_event.duration,
            )

            # R27
            planned = maintenance_event.starttime + maintenance_event.duration
            
            fo = amos.ForecastedOrder(
                workorderid=workorderid,
                aircraftregistration=aircraft_registration,
                executiondate=executiondate,
                executionplace=executionplace,
                workpackage=workpackageid,
                kind="Forecast",
                deadline=deadline,
                planned=planned,
                frequency=self.random_int(max=100),
                frequencyunits=self.frequency_units_kind(quality=quality),
                forecastedmanhours=self.random_int(max=20))
            return fo
        elif kind == "TechnicalLogBook":

            # R10
            mel = self.mel_category_kind(quality=quality)

            # R28
            reportingdate = maintenance_event.starttime
            
            # R29
            due = executiondate + self.mel_reporting_deadline_duration(mel_type=mel, quality=quality)

            tlb = amos.TechnicalLogbookOrder(
                workorderid=workorderid,
                aircraftregistration=aircraft_registration,
                executiondate=executiondate,
                executionplace=executionplace,
                workpackage=workpackageid,
                kind="TechnicalLogBook",
                reporteurclass=self.report_kind(quality=quality),
                reporteurid=self.reporter(quality=quality).reporteurid,
                reportingdate=reportingdate,
                due=due,
                deferred=self.generator.pybool(),
                mel=mel
            )

            return tlb 
        else:
            wo = amos.WorkOrder(
                workorderid=workorderid,
                aircraftregistration=aircraft_registration,
                executiondate=executiondate,
                executionplace=executionplace,
                workpackage=workpackageid,
                kind=self.work_order_kind(quality=quality)
            )
            
            return wo
        

    def forecasted_order(
        self,
        max_id: int = 9999,
        quality: str = "good",
        work_package: T.Optional[amos.Workpackage] = None,
        maintenance_event: T.Optional[amos.MaintenanceEvent] = None,
    ) -> amos.ForecastedOrder:

        fo = self.work_order(
            max_id=max_id, 
            quality=quality,
            work_package=work_package,
            maintenance_event=maintenance_event,
            kind="Forecast")

        return fo

    def technical_logbook_order(
        self,
        max_id: int = 9999,
        quality: str = "good",
        work_package: T.Optional[amos.Workpackage] = None,
        maintenance_event: T.Optional[amos.MaintenanceEvent] = None,
    ) -> amos.TechnicalLogbookOrder:

        tlb = self.work_order(
            max_id=max_id, 
            quality=quality,
            work_package=work_package,
            maintenance_event=maintenance_event,
            kind="TechnicalLogBook")

        return tlb

    def operational_interruption_event(
        self,
        max_id: int = 9999,
        slot: T.Optional[T.Union[aims.FlightSlot, aims.MaintenanceSlot]] = None,
        quality="good",
    ) -> amos.OperationalInterruption:
        """produces a random operational interruption

        An Operational Interruption is a maintenance event that occurs at
        a flight slot, and occasionates some kind of delay

        :return: an instance of OperationalInterruption
        :rtype: amos.OperationalInterruption
        """

        # if no slot is provided, then we generate one at random
        if slot is None:
            slot = self.random_element[self.flight_slot, self.maintenance_slot]()

        oi_starttime = slot.scheduleddeparture
        slot_kind = slot.kind
        oi_aircraftregistration = slot.aircraftregistration

        if slot_kind == "Flight":
            # R12-B departure is the scheduleddeparture
            departure = slot.scheduleddeparture

            # R13: Values can't be null, and must be the same as in the flight
            delay_code = slot.delaycode 

            if quality == "bad":
                airport = self.airport_code(quality=quality)
            elif quality == "noisy":
                airport = self.make_noisy(slot.departureairport, max_whitespace=2)
            else:
                airport = slot.departureairport

            flight_id = slot.flightid  # R12-C
            maintenanceeventkind = self.maintenance_event_kind(quality=quality, kind="Maintenance")

            duration = self.interruption_duration(
                interruption_type=maintenanceeventkind
            )

            # R8-A
            maintenance_id = "_".join(
                [
                    str(self.random_int(max=max_id)), 
                    str(oi_starttime + duration)]
            )
        else:
            # Then it is a MaintenanceSlot instance
            # and it produces a maintenance event
            # whose following attributes are not considered
            flight_id = self.flight_id(quality=quality)
            departure = 
            delay_code = None

            # R11-A, we set an airport at random
            airport = self.airport_code(quality=quality)

            maintenanceeventkind = self.maintenance_event_kind(
                quality=quality, kind = "Flight"
            )

            duration = self.interruption_duration(
                interruption_type=maintenanceeventkind
            )

            # R8-A
            maintenance_id = "_".join(
                [
                    str(self.random_int(max=max_id)), 
                    str(oi_starttime + duration)]
            )

        oi = amos.OperationalInterruption(
            maintenanceid=maintenance_id,
            aircraftregistration=oi_aircraftregistration,
            airport=airport,
            subsystem=self.ata_code(quality=quality),
            starttime=oi_starttime,
            duration=duration,
            kind=maintenanceeventkind,
            flightid=flight_id,
            departure=departure,
            delaycode=delay_code,  # R13
        )

        return oi

    def maintenance_event(
        self,
        max_id: int = 9999,
        slot: T.Optional[T.Union[aims.FlightSlot, aims.MaintenanceSlot]] = None,
        operational_interruption: T.Optional[amos.OperationalInterruption] = None,
        quality: str = "good",
    ) -> amos.MaintenanceEvent:
        """Produces a random maintenance event from a random operational interruption
        """

        oi = (operational_interruption or 
                self.operational_interruption_event(
                    max_id=max_id, 
                    slot=slot, 
                    quality=quality))

        return amos.MaintenanceEvent(
            maintenanceid=oi.maintenance_id,
            aircraftregistration=oi.aircraftregistration,
            airport=oi.airport,
            subsystem=oi.subsystem,
            starttime=oi.starttime,
            duration=oi.duration,
            kind=oi.kind,
        )

    # ---------------------------------------------------------------------------- #
    #                                     AIMS                                     #
    # ---------------------------------------------------------------------------- #

    def flight_id(self, quality="good") -> str:
        return self.flight_slot(quality=quality).flightid

    def flight_slot(self, *args, **kwargs) -> aims.FlightSlot:

        # args, kwargs unpacking
        cancelled = kwargs.pop("cancelled", None)
        config = kwargs.pop("config", {})
        manufacturer = kwargs.pop("manufacturer", None)
        quality = kwargs.pop("quality", "good")

        # TODO: remove these defaults and expose them at a higher level
        multiplier = 1 if quality in {"good", "noisy"} else self.random_int(5, 10)

        max_duration: int = config.get("max_duration", 5) * multiplier
        max_delay: int = config.get("max_delay", 40) * multiplier
        max_pas: int = config.get("max_pas", 180) * multiplier
        min_pas: int = config.get("min_pas", 90) * multiplier
        max_ccrew: int = config.get("max_ccrew", 4) * multiplier
        min_ccrew: int = config.get("min_ccrew", 3) * multiplier
        max_fcrew: int = config.get("max_fcrew", 3) * multiplier
        min_fcrew: int = config.get("min_fcrew", 2) * multiplier

        route: T.List[str] = self.flight_route()
        orig: str = (
            route[0] if quality == "good" else self.airport_code(quality=quality)
        )
        dest: str = (
            route[1] if quality == "good" else self.airport_code(quality=quality)
        )

        flight_number: str = self.flight_number(quality=quality)
        passengers: int = self.random_int(min=min_pas, max=max_pas)
        cabin_crew: int = self.random_int(min=min_ccrew, max=max_ccrew)
        flight_crew: int = self.random_int(min=min_fcrew, max=max_fcrew)

        # R19
        scheduled_departure: datetime = self.flight_timestamp(quality=quality)
        scheduled_arrival: datetime = scheduled_departure + self.duration(
            max_hours=max_duration
        )

        aircraft_registration: str = getattr(
            manufacturer, "aircraft_reg_code", None
        ) or self.aircraft_registration_code(quality=quality)

        if cancelled is None:
            cancelled = self.generator.pybool()

        # R22-B
        # if flight is cancelled, then some attributes must be empty
        if cancelled:
            delay = 0
            delay_code = None
            actual_arrival = None
            actual_departure = None
        else:
            delay = self.duration(max_minutes=max_delay)
            delay_code = self.delay_code(quality=quality)
            # R22
            actual_departure = scheduled_departure + delay
            actual_arrival = scheduled_arrival + delay

        # stfrtime uses here the format that was in the java code.
        # This date is not ISO 8601 compliant, but it could be set
        # as a config parameter later, I guess

        # rule R17, R12
        flight_id: str = "-".join(
            [
                scheduled_departure.strftime("%d%m%y"),
                orig,
                dest,
                flight_number,
                aircraft_registration,
            ]
        )

        if quality == "bad":
            # we swap order to corrupt data
            actual_departure, actual_arrival = actual_arrival, actual_departure
            aircraft_registration = self.aircraft_registration_code(quality=quality)

        return aims.FlightSlot(
            aircraftregistration=aircraft_registration,
            scheduleddeparture=scheduled_departure,
            scheduledarrival=scheduled_arrival,
            kind="Flight",
            flightid=flight_id,
            departureairport=orig,
            arrivalairport=dest,
            actualdeparture=actual_departure,
            actualarrival=actual_arrival,
            cancelled=cancelled,
            delaycode=delay_code,
            passengers=passengers,
            cabincrew=cabin_crew,
            flightcrew=flight_crew,
        )

    def maintenance_slot(self, *args, **kwargs) -> aims.MaintenanceSlot:

        flight_slot = kwargs.pop("flight_slot", None)
        fs = flight_slot or self.flight_slot(*args, **kwargs)

        return aims.MaintenanceSlot(
            aircraftregistration=fs.aircraftregistration,
            scheduleddeparture=fs.scheduled_departure,
            scheduledarrival=fs.scheduled_arrival,
            kind="Maintenance",
            programmed=self.generator.pybool(),
        )

    def slot(self, *args, **kwargs) -> aims.MaintenanceSlot:

        flight_slot = kwargs.pop("flight_slot", None)
        fs = flight_slot or self.flight_slot(*args, **kwargs)

        return aims.Slot(
            aircraftregistration=fs.aircraftregistration,
            scheduleddeparture=fs.scheduled_departure,
            scheduledarrival=fs.scheduled_arrival,
            kind=self.slot_kind(kwargs.get("quality", "good")),
        )


fake_airport = Faker()
fake_airport.add_provider(AirportProvider)