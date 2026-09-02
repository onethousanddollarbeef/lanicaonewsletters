#!/usr/bin/env python3
"""Build July 2026 newsletter data and patch site files."""

import json
import re
from pathlib import Path

try:
    from opencc import OpenCC
except ImportError:
    OpenCC = None

ROOT = Path(__file__).resolve().parents[1]

ZH_ARTICLES = [
    {
        "title": "2027财年H-1B抽签正式收官，确定没有海底捞",
        "paras": [
            "7月17日，移民局宣布已收到足够数量的H-1B配额申请，2027财年H-1B年度名额全部用尽，因此今年不会进行第二轮抽签。至此，2027财年H-1B抽签工作正式结束。",
            "今年是H-1B制度改革后的首个申请季。与往年随机抽签不同，国土安全部首次采用加权抽签规则，高薪岗位拥有更高的中签概率。",
            "根据移民局此前公布的数据，今年共收到211,600份有效注册，较上一财年的343,981份减少约38.5%；中签申请人中，71.5%拥有美国硕士及以上学历，而最低工资等级（Level 1）仅占全部中签注册的17.7%。这些数据反映出，新规则已明显提高高薪岗位及高学历申请人的竞争优势。",
            "值得注意的是，本次公告仅意味着年度配额H-1B申请正式结束。H-1B延期、雇主变更、申请修改以及部分免抽签H-1B申请仍可继续向移民局递交，不受本次配额用尽影响。",
        ],
    },
    {
        "title": "公共负担新规正式落地！领过政府福利或导致绿卡被拒",
        "paras": [
            "7月20日，国土安全部正式发布公共负担最终规则。公共负担是美国移民法规定的一项不可入境事由，适用于绝大多数职业移民和亲属移民申请人，如果政府认定申请人可能成为公共负担，其签证、入境或调整身份申请或被拒。",
            "新规要求移民官继续根据申请人的年龄、健康、家庭、财务状况、教育和职业技能进行整体评估，同时可进一步考虑申请人是否申请、获批或领取过收入或资产审查型政府福利。由于法规没有统一评分标准，也没有规定有利因素是否可以抵消不利因素，移民官将拥有更大的自由裁量权。",
            "新规将于2026年9月18日正式生效，移民局也将同步更新I-485身份调整申请表。申请人若仅因公共负担不具备入境资格，国土安全部仍可酌情允许其提交公共负担保证金。对于9月18日后提交的保证金，保证金有效期内如领取相关福利或违反条件，可能导致保证金被没收。",
            "保证金通常仅可在被担保人死亡、永久离境、入籍、由新保证金替代，或入境及调整身份满五年且未违约时解除。",
        ],
    },
    {
        "title": "留学生D/S正式取消，逾期立即累计非法滞留",
        "paras": [
            "7月17日，国土安全部发布最终规则，取消长期适用于F类国际学生、J类交流访问者及I类外国新闻媒体代表的“身份有效期（Duration of Status，D/S）”制度，改为明确合法停留期限。",
            "未来，F-1学生及家属、J-1交流访问者及家属最长可获批四年停留；I类外国媒体人员最长停留240天，持中国大陆护照者最长停留90天。如需延长学业项目和工作期限、开始OPT或转换学校，均需向移民局申请延期停留，并完成生物识别信息采集。",
            "如未在授权停留期限届满前及时提交延期申请，或延期申请被拒后仍未离境，则立刻开始累计非法居留时间，累计超过180天触发三年禁入美国，累计超过一年则面临十年禁入。",
            "此外，新规还进一步收紧了F-1身份管理，包括毕业后的60天宽限期缩短为30天，禁止本科生第一学年和研究生全学年内更换专业或教育层级，并禁止重复攻读同层级或降级学历项目。新规将于《联邦公报》发布60天后正式生效，相关个人、学校及雇主请及时调整规划。",
        ],
    },
    {
        "title": "突发！法院叫停部分移民新政：TPS工卡恢复，庇护年费处罚暂停",
        "paras": [
            "7月21日，马萨诸塞州联邦地区法院在 Venezuelan Association of Massachusetts v. USCIS 一案中发布行政暂缓令，临时停止执行部分大而美法案制定的移民政策。",
            "本次暂缓令首先涉及临时保护身份（TPS）持有人的工作许可。根据法院命令，此前已经获得自动延期的TPS工卡，将继续维持原先获准的到期日，部分原本可能提前失效的TPS工卡暂时恢复原有有效期限。",
            "法院同时暂停移民局因庇护申请人未缴纳庇护年费而采取不利措施。移民局暂时不得因申请人未缴纳庇护年费而拒绝其庇护申请；不得因未缴纳庇护年费而终止其工作许可；不得仅因申请人未缴纳庇护年费而启动递解程序。不过，法院并未禁止移民局继续收取庇护年费。收到移民局缴费通知的申请人，仍必须按照通知要求及时付款。",
            "此次裁定只是诉讼期间的临时行政措施，并非案件最终判决。法院预计将在听取双方更完整的意见后，作出进一步裁定。",
        ],
    },
    {
        "title": "EB-5新拟议规则公布，投资金额上涨至140万美元",
        "paras": [
            "7月2日，国土安全部在《联邦公报》刊登EB-5投资移民拟议新法规，并开放60天公众意见征集。拟议新规对投资资金、商业计划、资金处于风险状态及项目资金再部署等核心要求作出进一步说明。",
            "其中，部分高就业地区项目的最低投资额拟提高至140万美元，并允许政府每五年调整一次。投资人在递交申请时，资金必须已经实际投入或提供给创造就业实体使用，不能仅承诺未来投资。",
            "新规还将加强对区域中心和项目方的监管，把审计、文件保存、背景调查及违规处罚正式写入法规。区域中心原则上至少每五年接受一次政府审计，违规者可能面临罚款、暂停资格或取消资格。",
            "此外，国家安全、资金来源、项目选址及就业创造将成为未来审查重点，政府可能加强对基础设施项目、高失业率地区认定及项目参与人员背景的审查；对于项目发生重大变化的情况，新规也拟提供一定补救空间，帮助符合条件的投资人保留申请资格或优先日。",
            "目前，该规则仍处于意见征集阶段，最终内容及生效时间尚未确定，但已反映出USCIS未来将重点审查资金来源、项目选址、就业创造及国家安全等问题。",
        ],
    },
    {
        "title": "特朗普10万美元政策再遭重挫：上诉法院拒绝恢复收费",
        "paras": [
            "7月24日，H-1B 10万美元费用迎来最新进展。第一巡回联邦上诉法院拒绝特朗普政府此前提出的暂停执行请求，地区法院此前撤销收费政策的判决恢复生效，USCIS目前不得继续征收H-1B 10万美元费用。",
            "移民局预计将根据法院裁定更新H-1B申请指引和递交程序，但相关通知可能仍需数日才能发布。对于已经缴纳10万美元费用的雇主是否可以申请退款，目前也尚无明确说明。",
            "此次裁定并不代表案件已经结束。特朗普政府预计将继续就地区法院的判决提出上诉，10万美元收费政策最终是否会被彻底取消，仍有待后续诉讼结果。计划近期提交相关H-1B申请的雇主，应密切关注USCIS发布的最新操作指引。",
        ],
    },
    {
        "title": "ICE执法全面升级：逮捕与拘留人数双创新高",
        "paras": [
            "7月29日，ICE在社交平台X上表示有望连续第二个月刷新逮捕纪录。ICE称，目前的执法成果符合政府设定的目标，也是为应对前一届政府期间大量移民进入美国而采取的必要措施。",
            "据媒体报道，7月初短短五天内，超过10,000人被移民部门拘留。ICE每日逮捕人数由此前约1,000人上升至最高约2,400人，执法部门还要求将每日逮捕人数长期维持在至少2,000人。",
            "目前，超过80%的ICE工作人员已被调往逮捕行动，部分执法人员甚至需要每周工作七天，全美移民拘留人数也已增至约63,000人。",
            "随着执法节奏加快，相关个人和家庭应随身携带身份证明、案件材料及律师联系方式，并建立紧急联络安排，以便在突发执法行动中及时获得法律协助。",
        ],
    },
    {
        "title": "每天罚998美元！国土安全部利用每日民事罚款迫使“自行离境”",
        "paras": [
            "7月22日，国土安全部进一步扩大对收到最终递解令后仍留在美国人员的民事罚款措施。截至目前，ICE已发出超过10万份罚款通知，对符合条件的个人按每天998美元计算罚款。",
            "根据现行法律，罚款最长可追溯五年，累计金额最高可接近180万美元。根据目前政策，收到罚款通知的人员可在约15天内提出异议；如通过CBP Home程序主动离境，罚款可能获得豁免。",
            "若未及时处理，政府可能采取民事诉讼、债务催收、工资扣押、税款抵扣及信用记录等方式追缴欠款，并可能在未来移民申请中作为不利因素予以考虑。",
            "截至2026年7月中旬，ICE已累计发出超过103,000份罚款通知，总金额超过840亿美元。不过，目前实际收回的金额仍然有限。与此同时，多家法律组织已就该政策提起诉讼，主张其违反正当程序原则及美国宪法第八修正案关于禁止过度罚款的规定。",
        ],
    },
    {
        "title": "最新现行工资标准更新：拟议涨薪暂未落地",
        "paras": [
            "7月1日，劳工部更新全国现行工资数据库，为H-1B、PERM等就业类移民申请提供最新薪资标准。雇主和申请人可通过劳工部FLAG系统查询所在地区及职位对应的工资水平。",
            "今年3月，国土安全部曾提出H-1B薪资改革方案，计划大幅提高各级现行工资标准，其中Level 1拟提高至接近现行Level 2水平，Level 4则拟提高至行业约前12%的高薪水平。该拟议规则已于5月结束公众意见征集，但目前尚无进一步进展。",
            "此次劳工部发布的最新工资数据暂未体现上述改革，仍属于根据劳动力市场变化进行的年度例行调整。计划申请H-1B的雇主应及时核查最新工资标准并评估用工成本。",
            "对于现有H-1B员工，年度工资数据更新通常不会自动触发加薪义务，只要实际工资持续符合LCA及相关法规要求即可。H-1B薪资改革是否最终实施仍存在不确定性，后续仍需关注国土安全部公布的最新进展。",
        ],
    },
    {
        "title": "PERM迎20年来最大改革，招聘方式或将全面改写",
        "paras": [
            "本月，劳工部将《现代化PERM移民签证项目劳动力市场测试并加强美国工人保护》拟议规则列入联邦监管议程。这是劳工部自2004年以来首次计划对PERM进行全面改革。",
            "现行PERM制度已经实施超过20年，但美国招聘市场发生了巨大变化。企业招聘早已从传统报纸广告大量转向LinkedIn、Indeed等线上平台，而PERM部分招聘要求仍沿用二十年前的纸媒传播。",
            "同时，近年来PERM审理时间延长、文件要求增加，也使雇主为关键技术人才办理绿卡的周期进一步拉长。",
            "此次改革重点将放在更新招聘和劳动力市场测试标准、调整雇主招聘审核方式、加强美国工人保护及完善文件保存和合规要求等方面，使PERM制度更加符合当前招聘市场。改革一旦落地，雇主未来可能需要调整招聘程序，并保存更加完整的招聘、候选人筛选及拒绝美国求职者的相关记录，PERM申请的合规要求也可能进一步提高。",
            "目前，劳工部尚未公布拟议规则具体条文，在最终规则正式生效前，PERM申请流程和现行法规均不会发生变化，雇主仍应按照现行规定办理PERM申请。",
        ],
    },
    {
        "title": "移民拘留再收紧！长期居美也未必有资格保释",
        "paras": [
            "7月21日，第五巡回联邦上诉法院裁定，在案件上诉期间，政府可继续拘留三名无证移民，无需执行下级法院此前的释放命令。该裁定适用于路易斯安那州、密西西比州和得克萨斯州等第五巡回辖区。",
            "三名当事人均已在美国生活多年、无犯罪记录，并育有美国公民子女，但因早年未经许可入境被移民机关拘留。特朗普政府援引国土安全部2025年7月备忘录主张，此类人员原则上应被强制拘留，不能仅因长期居住、家庭关系或已提出移民申请而获得保释。",
            "目前，美国各联邦法院对此仍存在明显分歧。第五巡回和第八巡回法院的裁决整体更有利于政府，而加利福尼亚州、内华达州等地的联邦法院则曾要求为类似人员提供保释听证，或认定相关拘留做法违反宪法。",
            "随着不同巡回法院裁决持续分化，该问题未来可能提交美国最高法院统一裁决。",
        ],
    },
    {
        "title": "百名移民法官离职！司法独立与案件积压引担忧",
        "paras": [
            "联合国人权理事会任命的独立专家发表声明，对美国政府解职超过100名移民法官表示担忧，认为相关举措可能削弱司法独立，并影响移民法庭的案件处理能力。",
            "专家指出，部分法官可能因专业背景、过往裁决或被认为具有特定政治立场而遭解职，并担心移民审查执行办公室的职能定位可能发生变化，由原本相对中立的裁判机构，逐步转向更加侧重移民执法目标。",
            "根据美国移民律师协会统计，自2025年1月以来，全美约700名移民法官中，已有超过100人离职或被解职。法官人数减少可能进一步加剧案件积压，并导致重新分案、听证延期或审理法官变更。",
            "目前，已有多名前移民法官就解职决定提起诉讼，相关案件仍在审理过程中。",
        ],
    },
    {
        "title": "ICE大规模扩建拘留中心！地方政府开始出手阻拦",
        "paras": [
            "本月，移民及海关执法局（ICE）启动大规模扩充移民拘留设施的计划，拟在全美最多14个地点新建或扩建拘留中心，以提升移民拘留和递解能力。不过，该计划已在部分地区遭遇基础设施限制和行政审批阻力。",
            "公开信息显示，ICE正在向承包商征集方案，计划建设可容纳更多被拘留人员的大型拘留及处理中心，以配合移民执法行动。与此同时，新设施的医疗保障、人员配置、法律服务可及性及选址等问题也受到关注。",
            "部分拟建地点距离现有移民法律服务网络较远，可能增加被拘留人员获得法律援助的难度。宾夕法尼亚州政府日前拒绝为一处拟建拘留中心发放饮用水及污水处理许可证，理由是当地基础设施无法满足数千名被拘留人员的使用需求。ICE随后撤回相关行政申诉，该项目目前暂时搁置。",
        ],
    },
    {
        "title": "H-1B十万美元入境费后，其他签证也要交十万保证金？",
        "paras": [
            "7月16日，多家媒体报道称，特朗普政府正在研究一项新的移民签证保证金方案，拟要求部分通过美国驻外使领馆申请移民签证的申请人缴纳约10万美元的可退还保证金，以证明其具备经济自给能力，并降低其在成为美国永久居民后依赖政府公共资源的风险。",
            "该方案目前仍处于讨论阶段，保证金的具体金额、适用国家、适用申请人范围及实施方式均尚未最终确定，保证金也可能根据个案情况调整。",
            "这一方案并非全新的政策模式，而可能是在现有签证保证金试点基础上的进一步扩大。自2025年8月起，部分国家的旅游签证申请人已被要求缴纳最高15,000美元保证金；如出现逾期停留或入境后申请其他移民身份等情况，保证金可能被没收。",
            "目前，该试点项目已扩大至50个国家。",
        ],
    },
    {
        "title": "J-1新规酝酿收紧！保险断缴也可能被终止项目",
        "paras": [
            "国务院近日发布J-1交流访问项目拟议规则，并启动为期60天的公众意见征集。此次拟议规则拟扩大J-1项目被终止的适用情形，同时调整SEVIS管理要求，并与即将于9月15日生效的F/J/I固定停留期限新规进行衔接。",
            "根据拟议规则，J-1及J-2人员如未持续维持符合要求的医疗和意外保险，即使并非故意，也可能被Sponsor终止项目。申请人还必须持续提供真实、完整的信息和文件，如存在虚假、遗漏或不实，Sponsor也可能被要求终止其项目资格。",
            "国务院也拟扩大直接终止J-1项目的权限。若申请人的J-1签证被立即撤销，国务院可在无需提前通知、也无需给予申诉机会的情况下终止其交流项目；对于涉嫌提供虚假信息或未经授权工作的情况，则仍需向申请人发出通知，并给予提出异议的机会。",
            "目前，该规则仍处于拟议阶段，尚未正式生效。",
        ],
    },
    {
        "title": "美国对加拿大加征50%关税！贸易战火再升级",
        "paras": [
            "7月20日，特朗普总统签署多项公告，宣布自2026年8月19日起，对部分加拿大商品加征最高50%的关税，包括冰球用品、电子产品、蜂蜜、胶合板、珠宝、酒类及部分乳制品等。",
            "白宫表示，此次加征关税是对加拿大此前针对美国商品采取关税、进口限制及抵制美国酒类产品等措施的回应。美方认为，加拿大相关政策对美国贸易构成“不合理、不平等且具有歧视性”的待遇，因此决定依据《1930年关税法》第338条采取反制。该条款允许总统对歧视美国商业利益的国家征收最高50%的关税，据悉，这是美国首次以这种方式动用该条款。",
            "不过，美方表示仍愿意与加拿大继续谈判，并强调双方尚未正式进入贸易战。加拿大目前是美国第二大贸易伙伴，今年前五个月两国货物贸易额已超过3000亿美元。",
            "新关税一旦实施，可能进一步推高跨境贸易成本，并引发加拿大采取新一轮反制措施。双方能否在8月19日前通过谈判缓和争端，值得持续关注。",
        ],
    },
]

EN_ARTICLES = [
    {
        "title": "FY 2027 H-1B Lottery Concludes: No Second-Round Drawing",
        "paras": [
            "On July 17, USCIS announced that it had received a sufficient number of H-1B cap-subject petitions to reach the annual limit for fiscal year 2027. Because the FY 2027 H-1B cap has been fully used, there will be no second-round lottery this year. The FY 2027 H-1B lottery process is now officially complete.",
            "This was the first application season under the reformed H-1B system. Unlike prior years' random selection process, DHS used a weighted lottery for the first time, giving higher-wage positions a greater chance of selection.",
            "According to data USCIS released earlier, the agency received 211,600 valid registrations this year, down about 38.5% from 343,981 in the prior fiscal year. Among selected registrants, 71.5% held a U.S. master's degree or higher, while the lowest wage level (Level 1) accounted for only 17.7% of all selected registrations. These figures suggest the new rules have significantly strengthened the competitive position of higher-paid roles and more highly educated applicants.",
            "It is important to note that this announcement applies only to cap-subject H-1B petitions for the annual quota. H-1B extensions, employer changes, amended petitions, and certain cap-exempt H-1B filings may still be submitted to USCIS and are not affected by the cap being reached.",
        ],
    },
    {
        "title": "Public Charge Final Rule Takes Effect: Past Benefit Use May Jeopardize Green Cards",
        "paras": [
            "On July 20, DHS published the final public charge rule. Public charge is a ground of inadmissibility under U.S. immigration law that applies to most employment-based and family-based immigrants. If the government determines that an applicant is likely to become a public charge, the applicant's visa, admission, or adjustment of status application may be denied.",
            "The new rule requires immigration officers to continue conducting a totality-of-the-circumstances review based on age, health, family status, financial resources, education, and skills. Officers may also consider whether the applicant applied for, was approved for, or received means-tested public benefits. Because the regulation does not establish a uniform scoring system and does not specify whether positive factors can offset negative ones, adjudicators will have broader discretion.",
            "The rule takes effect on September 18, 2026, and USCIS will update Form I-485 accordingly. Applicants found inadmissible solely on public charge grounds may still be allowed to post a public charge bond at DHS's discretion. For bonds submitted after September 18, receipt of covered benefits or violation of bond conditions during the bond period may result in forfeiture.",
            "A bond may generally be released only upon the sponsored person's death, permanent departure, naturalization, substitution by a new bond, or after five years of admission or adjustment without default.",
        ],
    },
    {
        "title": "Duration of Status Eliminated for Students: Overstays Now Trigger Unlawful Presence",
        "paras": [
            "On July 17, DHS published a final rule eliminating the long-standing duration of status (D/S) policy for F-1 international students, J-1 exchange visitors, and I foreign media representatives, replacing it with fixed periods of authorized stay.",
            "Going forward, F-1 students and dependents and J-1 exchange visitors and dependents may receive up to four years of authorized stay. I foreign media representatives may receive up to 240 days, and holders of People's Republic of China passports may receive up to 90 days. Extensions for academic programs, work authorization, OPT, or school transfers will require USCIS approval and biometrics collection.",
            "If an extension is not filed before authorized stay expires, or if an extension is denied and the person does not depart, unlawful presence begins immediately. Unlawful presence of more than 180 days triggers a three-year bar, and more than one year triggers a ten-year bar.",
            "The rule also tightens F-1 status management, including shortening the post-completion grace period from 60 to 30 days, restricting major or degree-level changes during the first undergraduate year and throughout graduate study, and prohibiting repeated study at the same or lower degree level. The rule takes effect 60 days after publication in the Federal Register, and students, schools, and employers should plan accordingly.",
        ],
    },
    {
        "title": "Court Blocks Parts of New Immigration Policies: TPS Work Cards Restored, Asylum Fee Penalties Paused",
        "paras": [
            "On July 21, the U.S. District Court for the District of Massachusetts issued a temporary administrative stay in Venezuelan Association of Massachusetts v. USCIS, halting enforcement of certain immigration policies enacted under the One Big Beautiful Bill Act.",
            "The stay first affects work authorization for Temporary Protected Status (TPS) holders. Under the court's order, TPS work cards that had received automatic extensions will keep their previously approved expiration dates, and some cards that might otherwise have expired early will temporarily retain their original validity.",
            "The court also paused adverse USCIS actions based on failure to pay the annual asylum fee. USCIS may not deny asylum applications, terminate work authorization, or initiate removal proceedings solely because an applicant has not paid the asylum fee. However, the court did not prohibit USCIS from continuing to collect the fee. Applicants who receive a payment notice must still pay on time.",
            "This ruling is a temporary measure during litigation, not a final decision. The court is expected to issue further rulings after receiving more complete briefing from both sides.",
        ],
    },
    {
        "title": "Proposed EB-5 Rule Would Raise Investment Amount to $1.4 Million",
        "paras": [
            "On July 2, DHS published a proposed EB-5 rule in the Federal Register and opened a 60-day public comment period. The proposal further clarifies requirements for investment capital, business plans, capital at risk, and redeployment of project funds.",
            "Among other changes, the minimum investment for certain high-employment-area projects would rise to $1.4 million, with authority for the government to adjust the amount every five years. At filing, investors would need to show that funds have actually been deployed or made available to the job-creating entity, not merely promised for future investment.",
            "The proposal would also strengthen oversight of regional centers and project sponsors by codifying audit, recordkeeping, background-check, and penalty requirements. Regional centers would generally face government audits at least every five years, and violators could face fines, suspension, or termination.",
            "National security, source of funds, project location, and job creation are expected to receive greater scrutiny, including closer review of infrastructure projects, high-unemployment-area designations, and project participants. The proposal would also provide limited remedial options when projects change materially, helping qualifying investors preserve filing eligibility or priority dates.",
            "The rule remains in the comment stage, and its final content and effective date are not yet known. It nonetheless signals USCIS's future focus on source of funds, project location, job creation, and national security.",
        ],
    },
    {
        "title": "Trump's $100,000 H-1B Fee Suffers Another Setback: Appeals Court Refuses to Reinstate Charge",
        "paras": [
            "On July 24, the H-1B $100,000 fee dispute reached a new stage. The U.S. Court of Appeals for the First Circuit denied the Trump administration's request to stay enforcement, allowing the district court's vacatur to take effect. USCIS may not continue collecting the $100,000 H-1B fee at this time.",
            "USCIS is expected to update H-1B filing guidance and procedures in light of the ruling, though updated instructions may take several days to publish. It remains unclear whether employers that already paid the $100,000 fee may seek refunds.",
            "The litigation is not over. The administration is expected to appeal further, and whether the $100,000 fee will ultimately be reinstated depends on later court rulings. Employers planning near-term H-1B filings should monitor USCIS guidance closely.",
        ],
    },
    {
        "title": "ICE Enforcement Surges: Arrests and Detention Reach New Highs",
        "paras": [
            "On July 29, ICE said on X that it was on track to set arrest records for a second consecutive month. ICE described the results as aligned with administration goals and as necessary to address large-scale migration during the prior administration.",
            "Media reports indicate that more than 10,000 people were detained by immigration authorities in just five days in early July. Daily ICE arrests rose from roughly 1,000 to as many as 2,400, and enforcement agencies have sought to maintain at least 2,000 arrests per day.",
            "More than 80% of ICE personnel have reportedly been reassigned to arrest operations, with some officers working seven days a week. Nationwide immigration detention has climbed to about 63,000 people.",
            "As enforcement accelerates, affected individuals and families should carry identification, case documents, and attorney contact information, and establish emergency communication plans to obtain legal help quickly if enforcement action occurs.",
        ],
    },
    {
        "title": "$998-a-Day Fines: DHS Uses Civil Penalties to Push 'Voluntary Departure'",
        "paras": [
            "On July 22, DHS expanded civil fines against individuals who remain in the United States after receiving final orders of removal. ICE has issued more than 100,000 fine notices, assessing eligible individuals at $998 per day.",
            "Under current law, fines may be assessed retroactively for up to five years, with cumulative amounts approaching $1.8 million. Recipients generally have about 15 days to contest a notice, and fines may be waived if the person departs voluntarily through the CBP Home program.",
            "If fines are not addressed, the government may pursue civil litigation, debt collection, wage garnishment, tax offsets, and credit reporting, and may treat unpaid fines as a negative factor in future immigration applications.",
            "As of mid-July 2026, ICE had issued more than 103,000 fine notices totaling more than $84 billion, though actual collections remain limited. Several legal organizations have challenged the policy, arguing that it violates due process and the Eighth Amendment's prohibition on excessive fines.",
        ],
    },
    {
        "title": "Prevailing Wage Data Updated: Proposed Pay Increases Not Yet Implemented",
        "paras": [
            "On July 1, the Department of Labor updated the national prevailing wage database used for H-1B, PERM, and other employment-based immigration filings. Employers and applicants can check wage levels by location and occupation through DOL's FLAG system.",
            "In March, DHS proposed an H-1B wage reform that would significantly raise prevailing wage levels, including moving Level 1 close to current Level 2 and Level 4 to roughly the top 12% of industry wages. That proposed rule closed for public comment in May, but no further action has been announced.",
            "The July wage release does not reflect those proposed reforms and remains a routine annual update based on labor-market changes. Employers planning H-1B filings should review the latest wage levels and assess labor costs.",
            "For current H-1B employees, annual wage updates generally do not automatically require pay increases so long as actual wages continue to satisfy LCA and related requirements. Whether the proposed H-1B wage reform will take effect remains uncertain.",
        ],
    },
    {
        "title": "Biggest PERM Overhaul in 20 Years May Rewrite Recruitment Requirements",
        "paras": [
            "This month, DOL placed a proposed rule titled Modernizing PERM Immigration Visa Program Labor Market Testing and Strengthening Protections for U.S. Workers on the federal regulatory agenda. It would be DOL's first comprehensive PERM overhaul since 2004.",
            "The current PERM system has been in place for more than 20 years, while U.S. hiring practices have changed dramatically. Recruitment has shifted from newspaper advertising to online platforms such as LinkedIn and Indeed, yet some PERM recruitment requirements still reflect paper-era practices.",
            "Longer PERM processing times and increased documentation demands have also lengthened the green card timeline for critical talent.",
            "The reform is expected to update recruitment and labor-market testing standards, revise employer recruitment review procedures, strengthen protections for U.S. workers, and improve recordkeeping and compliance requirements so PERM better matches today's hiring market. If finalized, employers may need to adjust recruitment procedures and maintain more complete records on outreach, candidate screening, and rejection of U.S. workers.",
            "DOL has not yet published the proposed rule text. Until a final rule takes effect, current PERM procedures and regulations remain unchanged, and employers should continue filing under existing requirements.",
        ],
    },
    {
        "title": "Detention Rules Tighten: Long-Term U.S. Residents May Still Be Denied Bond",
        "paras": [
            "On July 21, the U.S. Court of Appeals for the Fifth Circuit ruled that the government may continue detaining three undocumented immigrants during appeal without complying with lower-court release orders. The decision applies within the Fifth Circuit, including Louisiana, Mississippi, and Texas.",
            "All three individuals had lived in the United States for many years without criminal records and have U.S. citizen children, but were detained because they entered without authorization years ago. The Trump administration relied on a July 2025 DHS memorandum arguing that such individuals should generally be subject to mandatory detention and should not receive bond based on long residence, family ties, or pending immigration applications.",
            "Federal courts remain divided. The Fifth and Eighth Circuits have generally sided with the government, while courts in California, Nevada, and elsewhere have required bond hearings or found similar detention practices unconstitutional.",
            "As circuit splits deepen, the issue may eventually reach the U.S. Supreme Court.",
        ],
    },
    {
        "title": "More Than 100 Immigration Judges Leave the Bench, Raising Backlog Concerns",
        "paras": [
            "An independent expert appointed by the UN Human Rights Council expressed concern over the U.S. government's removal of more than 100 immigration judges, warning that the move could weaken judicial independence and reduce the immigration courts' capacity to handle cases.",
            "The expert said some judges may have been removed because of professional background, prior rulings, or perceived political views, and expressed concern that the Executive Office for Immigration Review could shift from a relatively neutral adjudicatory role toward a more enforcement-oriented mission.",
            "According to the American Immigration Lawyers Association, more than 100 of the nation's roughly 700 immigration judges have left or been removed since January 2025. Fewer judges may worsen case backlogs and lead to reassignment, hearing delays, and changes in presiding judges.",
            "Several former immigration judges have filed lawsuits challenging their removals, and those cases remain pending.",
        ],
    },
    {
        "title": "ICE Plans Major Detention Expansion as Local Governments Push Back",
        "paras": [
            "This month, ICE launched a large-scale plan to expand immigration detention capacity at up to 14 sites nationwide. The initiative has already encountered infrastructure limits and permitting obstacles in some areas.",
            "Public information indicates ICE is soliciting contractor proposals for larger detention and processing centers to support expanded enforcement. Questions remain about medical care, staffing, legal access, and site selection.",
            "Some proposed locations are far from existing immigration legal services networks, which could make it harder for detainees to obtain counsel. Pennsylvania recently denied water and sewage permits for one proposed facility, finding local infrastructure inadequate for housing thousands of detainees. ICE later withdrew its administrative appeal, and that project is currently on hold.",
        ],
    },
    {
        "title": "After the $100,000 H-1B Fee, Could Other Visas Require a $100,000 Bond?",
        "paras": [
            "On July 16, multiple media outlets reported that the Trump administration is considering a new immigrant visa bond program that would require certain consular applicants to post a refundable bond of about $100,000 to demonstrate self-sufficiency and reduce the risk of future reliance on public resources after becoming permanent residents.",
            "The proposal remains under discussion. The bond amount, covered countries, applicant scope, and implementation details have not been finalized and may vary by case.",
            "The idea would build on an existing visa bond pilot. Since August 2025, some tourist visa applicants from certain countries have been required to post bonds of up to $15,000, which may be forfeited for overstays or later immigration filings. That pilot has expanded to 50 countries.",
        ],
    },
    {
        "title": "Proposed J-1 Rule Would Tighten Program Termination, Including for Lapsed Insurance",
        "paras": [
            "The Department of State recently published a proposed J-1 exchange visitor rule and opened a 60-day comment period. The proposal would expand grounds for program termination, adjust SEVIS requirements, and align with fixed-stay rules for F, J, and I nonimmigrants taking effect September 15.",
            "Under the proposal, J-1 and J-2 participants who fail to maintain required medical and accident insurance—even unintentionally—could have their programs terminated by sponsors. Participants must also continue providing truthful and complete information; sponsors may be required to terminate programs based on false, omitted, or misleading information.",
            "State also proposes broader authority to terminate J-1 programs directly. If a J-1 visa is immediately revoked, State could terminate the exchange program without advance notice or an appeal opportunity. For suspected fraud or unauthorized employment, notice and an opportunity to respond would still be required.",
            "The rule remains proposed and has not taken effect.",
        ],
    },
    {
        "title": "U.S. Imposes 50% Tariffs on Canada as Trade Tensions Escalate",
        "paras": [
            "On July 20, President Trump signed proclamations imposing tariffs of up to 50% on certain Canadian goods beginning August 19, 2026, including hockey equipment, electronics, honey, plywood, jewelry, alcohol, and some dairy products.",
            "The White House said the tariffs respond to Canadian measures against U.S. goods, import restrictions, and boycotts of U.S. alcohol. The administration argued that Canada's actions constitute unreasonable, unequal, and discriminatory treatment and invoked Section 338 of the Tariff Act of 1930, which authorizes tariffs of up to 50% against countries that discriminate against U.S. commerce. Reports indicate this is the first time the United States has used the provision in this manner.",
            "The administration also said it remains open to negotiations and emphasized that the two countries have not formally entered a trade war. Canada is the United States' second-largest trading partner, with bilateral goods trade exceeding $300 billion in the first five months of this year.",
            "If implemented, the tariffs could raise cross-border costs and prompt new Canadian countermeasures. Whether the two governments can ease the dispute before August 19 remains uncertain.",
        ],
    },
]


def to_traditional(articles):
    if OpenCC is None:
        raise RuntimeError("opencc is required for Traditional Chinese conversion")
    converter = OpenCC("s2twp")
    converted = []
    for article in articles:
        converted.append(
            {
                "title": converter.convert(article["title"]),
                "paras": [converter.convert(p) for p in article["paras"]],
            }
        )
    return converted


def patch_july_html(data):
    path = ROOT / "july-2026.html"
    html = path.read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    html, count = re.subn(
        r'(<script id="july-newsletter-data" type="application/json">\n).*?(\n</script>)',
        rf"\1{payload}\2",
        html,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError("Failed to patch july-newsletter-data")
    path.write_text(html, encoding="utf-8")


def remove_briefs_from_index():
    path = ROOT / "index.html"
    html = path.read_text(encoding="utf-8")

    html = re.sub(
        r'\s*<a href="#briefs" data-i18n="navBriefs">Briefs</a>\n',
        "\n",
        html,
        count=1,
    )

    html = re.sub(
        r'\s*<section class="briefs-section" id="briefs"[\s\S]*?</section>\n',
        "\n",
        html,
        count=1,
    )

  # Remove brief-related translation keys
    for key in [
        "navBriefs",
        "briefsKicker",
        "briefsTitle",
        "briefsSource",
        "briefsSourceLink",
        "briefsUpdated",
        "briefOneDate",
        "briefOneTitle",
        "briefOneBody",
        "briefTwoDate",
        "briefTwoTitle",
        "briefTwoBody",
        "briefThreeDate",
        "briefThreeTitle",
        "briefThreeBody",
    ]:
        html = re.sub(rf'^\s*{key}:.*,\n', "", html, flags=re.M)

    html = re.sub(
        r"\s*const briefFeedUrl = .*?;\n",
        "",
        html,
        count=1,
    )
    html = re.sub(
        r"\s*const visibleBriefCount = .*?;\n",
        "",
        html,
        count=1,
    )
    html = re.sub(r"\s*let briefFeed = .*?;\n", "", html, count=1)

    html = re.sub(
        r"\n\s*function renderBriefs\(language\) \{[\s\S]*?\n\s*\}\n",
        "\n",
        html,
        count=1,
    )
    html = re.sub(
        r"\n\s*async function loadBriefs\(\) \{[\s\S]*?\n\s*\}\n",
        "\n",
        html,
        count=1,
    )
    html = re.sub(r"\n\s*renderBriefs\(activeLanguage\);\n", "\n", html, count=1)
    html = re.sub(r"\n\s*loadBriefs\(\);\n", "\n", html, count=1)

    html = html.replace(
        "editorials, and brief U.S. news summaries.",
        "editorials, and monthly newsletter issues.",
    )
    html = html.replace(
        "专题评论和美国重要新闻简报。",
        "专题评论和月刊内容。",
    )
    html = html.replace(
        "專題評論和美國重要新聞簡報。",
        "專題評論和月刊內容。",
    )

    summaries = {
        "en": "This issue covers H-1B cap results, public charge reforms, student visa changes, ICE enforcement, detention policy, wage updates, PERM reform, and major trade developments from July 2026.",
        "zhHans": "本期涵盖2026年7月H-1B抽签收官、公共负担新规、留学生身份调整、ICE执法升级、民事罚款、工资标准更新、PERM改革及美加关税等重要动态。",
        "zhHant": "本期涵蓋2026年7月H-1B抽籤收官、公共負擔新規、留學生身分調整、ICE執法升級、民事罰款、工資標準更新、PERM改革及美加關稅等重要動態。",
    }
    for lang, summary in summaries.items():
        html = re.sub(
            rf'(issueSummary: ")[^"]*(".*?# {lang})',
            rf"\1{summary}\2",
            html,
            count=1,
        )

    # Simpler direct replacements for issue summaries
    html = html.replace(
        "The July 2026 edition is being prepared. Articles covering the month's immigration, regulatory, and policy developments will appear here once the issue is finalized.",
        summaries["en"],
    )
    html = html.replace(
        "2026 年 7 月刊正在筹备中。涵盖本月移民、监管与政策动态的文章将在定稿后于此发布。",
        summaries["zhHans"],
    )
    html = html.replace(
        "2026 年 7 月刊正在籌備中。涵蓋本月移民、監管與政策動態的文章將在定稿後於此發布。",
        summaries["zhHant"],
    )

    path.write_text(html, encoding="utf-8")


def remove_briefs_from_july_page():
    path = ROOT / "july-2026.html"
    html = path.read_text(encoding="utf-8")
    html = re.sub(
        r'\s*<a href="\./#briefs" data-i18n="navBriefs">Briefs</a>\n',
        "\n",
        html,
        count=1,
    )
    path.write_text(html, encoding="utf-8")


def main():
    data = {
        "en": EN_ARTICLES,
        "zhHans": ZH_ARTICLES,
        "zhHant": to_traditional(ZH_ARTICLES),
    }
    patch_july_html(data)
    remove_briefs_from_index()
    remove_briefs_from_july_page()

    header_path = ROOT / "july-2026.html"
    header_html = header_path.read_text(encoding="utf-8")
    header_html = header_html.replace(
        "本期正在筹备中，2026 年 7 月刊的文章将于近期发布。",
        "",
    )
    header_html = header_html.replace(
        "本期正在籌備中，2026 年 7 月刊的文章將於近期發布。",
        "",
    )
    header_html = header_html.replace(
        "This issue is being prepared. Articles for the July 2026 edition will be published here shortly.",
        "",
    )
    header_path.write_text(header_html, encoding="utf-8")

    news_feed = ROOT / "news-feed.json"
    if news_feed.exists():
        news_feed.unlink()

    print(f"Built July newsletter with {len(ZH_ARTICLES)} articles in 3 languages.")


if __name__ == "__main__":
    main()
