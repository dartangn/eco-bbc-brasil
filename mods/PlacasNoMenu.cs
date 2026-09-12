// Servidor BBC-Brasil -- item "Icones para placa" no menu da esquerda do painel web (porta 27041).
//
// O painel web do Eco lista no menu lateral todo plugin que implementa IWebPlugin; e assim que o GoodPrice
// aparece la. A galeria em si ja e servida como pasta estatica do painel (WebClient/WebBin/placas -> /placas/),
// entao este arquivo so acrescenta o item de menu que abre aquela pagina.
//
// ============ O QUE DERRUBOU O SERVIDOR EM 10/09/2026 04:08, e como este arquivo foi refeito ============
// A primeira versao herdava de Singleton<T> e importava so Eco.Core.Utils. Resultado:
//     PlacasNoMenu.cs(27,39): error CS0246: o tipo ou namespace "Singleton<>" nao pode ser encontrado
// Tres arranques falhos, StartLimitBurst=3, start bloqueado por 30 min. Eu havia copiado a FORMA da classe de
// dois plugins publicos sem conferir em que namespace cada tipo vive.
// Esta versao NAO usa Singleton: ela existe para dar o acessador estatico .Obj, que aqui nao e usado, e era o
// unico tipo que eu nao conseguia localizar com certeza. A forma agora vem de arquivos que COMPILAM NESTE
// SERVIDOR, conferidos em 10/09/2026:
//     UserCode/StarterRewards/StarterRewardsPlugin.cs  class X : IModKitPlugin, IServerPlugin,
//                                                      IInitializablePlugin  -- sem classe base;
//                                                      usings Eco.Core.Plugins.Interfaces e Eco.Core.Utils
//     __core__/ChatLog/ChatLogger.cs                   GetCategory/GetStatus/Initialize(TimedTask), e
//                                                      Localizer com using Eco.Shared.Localization
//     UserCode/KabongBrasil/CustoEstrelas.cs           Localizer.DoStr e System.IO.File.AppendAllText
// Todo tipo usado aqui, menos IWebPlugin, aparece em pelo menos um arquivo que ja compila neste servidor.
//
// Membros das interfaces, conferidos na documentacao oficial (docs.play.eco, 10/09/2026):
//   IModKitPlugin : IServerPlugin         string GetStatus(), string GetCategory()
//   IInitializablePlugin : IServerPlugin  void Initialize(TimedTask timer)
//   IWebPlugin (Eco.Core.Plugins.Interfaces, NAO herda IServerPlugin)  LocString GetMenuTitle(),
//     string GetPluginIndexUrl(), string GetFontAwesomeIcon(), string GetStaticFilesPath(),
//     string GetEmbeddedResourceNamespace()
//
// AVISO da propria documentacao do IWebPlugin: "It is not recommended to write IWebPlugin implementations that
// are not compiled to a DLL assembly prior to server start." Este arquivo E compilado em UserCode. Se compilar
// e o item ainda nao aparecer no menu, e essa a razao, e o passo seguinte e empacotar em DLL. Nao afeta o jogo:
// IWebPlugin so mexe no painel web.
//
// Prova de vida: /opt/eco/placas-menu-vida.txt, uma linha por arranque, escrita por Initialize.
// REGRA 18: instalar SO imediatamente antes de um reinicio que alguem vai VIGIAR.
namespace Eco.Mods.KabongBrasil
{
    using Eco.Core.Plugins.Interfaces;   // IModKitPlugin, IServerPlugin, IInitializablePlugin, IWebPlugin
    using Eco.Core.Utils;                // TimedTask
    using Eco.Shared.Localization;       // LocString, Localizer

    public class PlacasNoMenuPlugin : IModKitPlugin, IServerPlugin, IInitializablePlugin, IWebPlugin
    {
        public string GetCategory() => "Mods";

        public string GetStatus() => string.Empty;

        public LocString GetMenuTitle() => Localizer.DoStr("Icones para placa");

        // O cliente web monta  <iframe src="/plugins/" + PluginIndexUrl>  (lido no app.5f7a279b.js do WebBin).
        // Por isso a URL e RELATIVA com "..": /plugins/../placas/index.html, que o navegador resolve para
        // /placas/index.html, a pasta estatica que o painel ja serve. Um "/placas/..." absoluto viraria
        // /plugins//placas/... e daria 404.
        public string GetPluginIndexUrl() => "../placas/index.html";

        // ICONE DO ITEM NO MENU. Em 10/09/2026 a primeira versao devolveu "fa-solid fa-image" e o item
        // apareceu SEM icone, ao contrario dos vizinhos. Motivo: "fa-solid" e sintaxe do Font Awesome 5/6, e
        // o painel embute o **Font Awesome 4.7.0** -- esta escrito no proprio CSS dele:
        //   WebClient/WebBin/css/chunk-vendors.5a691ece.css:  "Font Awesome 4.7.0 by @davegandy"
        // No 4.7 a classe e "fa fa-<nome>". O valor abaixo copia a forma do GoodPrice, que renderiza o
        // icone de etiqueta no mesmo menu; o valor dele, lido das strings UTF-16 da GoodPrice.dll, e
        // exatamente "fa fa-fw fa-tag". O "fa-fw" e largura fixa, e o que alinha o icone com os vizinhos.
        // "fa-map-signs" (placa de sinalizacao) existe no 4.7: conferido varrendo os seletores .fa-*:before
        // do CSS do painel, que tem 786 nomes. Outros que existem, se um dia quiser trocar: fa-picture-o,
        // fa-image, fa-photo, fa-paint-brush, fa-font, fa-language.
        public string GetFontAwesomeIcon() => "fa fa-fw fa-map-signs";

        // Nulos de proposito: nao ha arquivo nosso para o painel servir, nem recurso embutido em DLL.
        // A documentacao chama os dois de opcionais.
        public string GetStaticFilesPath() => null;

        public string GetEmbeddedResourceNamespace() => null;

        public void Initialize(TimedTask timer)
        {
            try
            {
                System.IO.File.AppendAllText("/opt/eco/placas-menu-vida.txt",
                    System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
                    + "  PlacasNoMenu ativo: menu -> /placas/index.html\n");
            }
            catch { }
        }
    }
}
