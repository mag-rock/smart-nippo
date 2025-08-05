# CLIライブラリとインタラクティブ機能の比較

## 概要
各言語のCLIフレームワークと、日報入力でのインタラクティブな機能（日付選択、補完、プロンプト等）の実装方法を比較します。

## 1. Python

### CLIフレームワーク

#### Typer（推奨）
```python
import typer
from typing import Optional
from datetime import date

app = typer.Typer()

@app.command()
def create(
    date: Optional[date] = typer.Option(None, help="日報の日付"),
    project: str = typer.Option(..., prompt="プロジェクト名を入力してください")
):
    """日報を作成します"""
    typer.echo(f"日報を作成: {date or '今日'} - {project}")

if __name__ == "__main__":
    app()
```

#### Click
```python
import click

@click.command()
@click.option('--date', type=click.DateTime(['%Y-%m-%d']))
@click.option('--project', prompt='プロジェクト名')
def create(date, project):
    """日報を作成します"""
    click.echo(f"日報を作成: {date} - {project}")
```

### インタラクティブ機能

#### Rich + Prompt Toolkit（最強の組み合わせ）
```python
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator
import questionary

console = Console()

# 1. Rich - 美しい表示
def show_calendar():
    table = Table(title="2024年1月")
    table.add_column("日", style="red")
    table.add_column("月")
    # ... カレンダー表示
    console.print(table)

# 2. Prompt Toolkit - 高度な入力
date_completer = WordCompleter(['2024-01-01', '2024-01-02', '2024-01-03'])
selected_date = prompt('日付を選択: ', completer=date_completer)

# 3. Questionary - 簡単な選択UI
date = questionary.select(
    "日付を選択してください:",
    choices=['2024-01-01', '2024-01-02', '2024-01-03']
).ask()

# 4. InquirerPy - より高度な選択
from InquirerPy import inquirer
from InquirerPy.base.control import Choice

date = inquirer.select(
    message="日付を選択:",
    choices=[
        Choice(value="2024-01-01", name="2024-01-01 (月) ✓"),
        Choice(value="2024-01-02", name="2024-01-02 (火)"),
    ],
    default="2024-01-01",
).execute()
```

#### カレンダー選択の実装例
```python
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
import keyboard  # pip install keyboard

class DatePicker:
    def __init__(self):
        self.console = Console()
        self.selected_date = datetime.now()
        
    def show(self):
        while True:
            self.display_calendar()
            key = keyboard.read_key()
            
            if key == "left":
                self.selected_date -= timedelta(days=1)
            elif key == "right":
                self.selected_date += timedelta(days=1)
            elif key == "up":
                self.selected_date -= timedelta(days=7)
            elif key == "down":
                self.selected_date += timedelta(days=7)
            elif key == "enter":
                return self.selected_date
            elif key == "esc":
                return None
```

## 2. Go

### CLIフレームワーク

#### Cobra（最も人気）
```go
package cmd

import (
    "github.com/spf13/cobra"
    "time"
)

var rootCmd = &cobra.Command{
    Use:   "smart-nippo",
    Short: "日報入力支援ツール",
}

var createCmd = &cobra.Command{
    Use:   "create",
    Short: "日報を作成",
    Run: func(cmd *cobra.Command, args []string) {
        date, _ := cmd.Flags().GetString("date")
        // 処理
    },
}

func init() {
    createCmd.Flags().StringP("date", "d", "", "日報の日付")
    rootCmd.AddCommand(createCmd)
}
```

#### urfave/cli
```go
package main

import (
    "github.com/urfave/cli/v2"
)

func main() {
    app := &cli.App{
        Name: "smart-nippo",
        Commands: []*cli.Command{
            {
                Name: "create",
                Flags: []cli.Flag{
                    &cli.StringFlag{
                        Name:    "date",
                        Aliases: []string{"d"},
                    },
                },
                Action: createReport,
            },
        },
    }
    app.Run(os.Args)
}
```

### インタラクティブ機能

#### Survey（Go版Inquirer）
```go
package main

import "github.com/AlecAivazis/survey/v2"

func selectDate() string {
    dates := []string{
        "2024-01-01 (月)",
        "2024-01-02 (火)",
        "2024-01-03 (水)",
    }
    
    var selected string
    prompt := &survey.Select{
        Message: "日付を選択してください:",
        Options: dates,
    }
    survey.AskOne(prompt, &selected)
    return selected
}

// より高度な例
func createReport() {
    qs := []*survey.Question{
        {
            Name: "date",
            Prompt: &survey.Select{
                Message: "日付を選択:",
                Options: generateDateOptions(),
                Default: "今日",
            },
        },
        {
            Name: "project",
            Prompt: &survey.Input{
                Message: "プロジェクト名:",
                Suggest: func(toComplete string) []string {
                    // 自動補完
                    return []string{"ProjectA", "ProjectB"}
                },
            },
        },
        {
            Name: "content",
            Prompt: &survey.Multiline{
                Message: "作業内容:",
            },
        },
    }
    
    answers := struct {
        Date    string
        Project string
        Content string
    }{}
    
    survey.Ask(qs, &answers)
}
```

#### Bubble Tea（よりカスタマイズ可能）
```go
package main

import (
    "github.com/charmbracelet/bubbletea"
    "github.com/charmbracelet/lipgloss"
)

type model struct {
    choices  []string
    cursor   int
    selected map[int]struct{}
}

func (m model) Init() tea.Cmd {
    return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case tea.KeyMsg:
        switch msg.String() {
        case "up", "k":
            if m.cursor > 0 {
                m.cursor--
            }
        case "down", "j":
            if m.cursor < len(m.choices)-1 {
                m.cursor++
            }
        case "enter", " ":
            _, ok := m.selected[m.cursor]
            if ok {
                delete(m.selected, m.cursor)
            } else {
                m.selected[m.cursor] = struct{}{}
            }
        }
    }
    return m, nil
}
```

## 3. Node.js

### CLIフレームワーク

#### Commander.js
```javascript
const { Command } = require('commander');
const program = new Command();

program
  .name('smart-nippo')
  .description('日報入力支援ツール')
  .version('1.0.0');

program.command('create')
  .description('日報を作成')
  .option('-d, --date <date>', '日報の日付')
  .option('-p, --project <project>', 'プロジェクト名')
  .action((options) => {
    console.log('日報作成:', options);
  });

program.parse();
```

#### Yargs
```javascript
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

yargs(hideBin(process.argv))
  .command('create', '日報を作成', (yargs) => {
    return yargs
      .option('date', {
        alias: 'd',
        describe: '日報の日付',
      })
  }, (argv) => {
    console.log('日報作成:', argv);
  })
  .parse();
```

### インタラクティブ機能

#### Inquirer.js（最も人気）
```javascript
const inquirer = require('inquirer');
const DatePrompt = require('inquirer-date-prompt');

inquirer.registerPrompt('date', DatePrompt);

async function createReport() {
  const answers = await inquirer.prompt([
    {
      type: 'date',
      name: 'date',
      message: '日付を選択:',
      format: { month: 'short', hour: undefined, minute: undefined },
      clearable: true,
    },
    {
      type: 'list',
      name: 'project',
      message: 'プロジェクトを選択:',
      choices: ['ProjectA', 'ProjectB', 'ProjectC'],
    },
    {
      type: 'editor',
      name: 'content',
      message: '作業内容を入力:',
    }
  ]);
  
  return answers;
}
```

#### Prompts（より軽量）
```javascript
const prompts = require('prompts');

const questions = [
  {
    type: 'date',
    name: 'date',
    message: '日付を選択してください',
    initial: new Date(),
    mask: 'YYYY-MM-DD'
  },
  {
    type: 'autocomplete',
    name: 'project',
    message: 'プロジェクトを選択',
    choices: [
      { title: 'Project A', value: 'proj-a' },
      { title: 'Project B', value: 'proj-b' }
    ]
  }
];

const response = await prompts(questions);
```

#### Blessed（フルスクリーンTUI）
```javascript
const blessed = require('blessed');

const screen = blessed.screen({
  smartCSR: true,
  title: '日報入力'
});

const calendar = blessed.box({
  top: 'center',
  left: 'center',
  width: '50%',
  height: '50%',
  content: 'カレンダー表示',
  tags: true,
  border: {
    type: 'line'
  },
  style: {
    border: {
      fg: '#f0f0f0'
    }
  }
});

screen.append(calendar);
screen.key(['escape', 'q', 'C-c'], () => process.exit(0));
screen.render();
```

## 4. Rust

### CLIフレームワーク

#### Clap（最も人気）
```rust
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "smart-nippo")]
#[command(about = "日報入力支援ツール")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Create {
        #[arg(short, long)]
        date: Option<String>,
        #[arg(short, long)]
        project: Option<String>,
    },
}
```

### インタラクティブ機能

#### Dialoguer（Rust版Inquirer）
```rust
use dialoguer::{theme::ColorfulTheme, Select, Input, Editor, Confirm};
use chrono::{Local, Duration};

fn select_date() -> String {
    let dates: Vec<String> = (0..7)
        .map(|i| {
            let date = Local::now() - Duration::days(i);
            date.format("%Y-%m-%d (%a)").to_string()
        })
        .collect();
    
    let selection = Select::with_theme(&ColorfulTheme::default())
        .with_prompt("日付を選択してください")
        .items(&dates)
        .default(0)
        .interact()
        .unwrap();
    
    dates[selection].clone()
}

fn create_report() {
    let date = select_date();
    
    let project = Input::<String>::new()
        .with_prompt("プロジェクト名")
        .interact_text()
        .unwrap();
    
    let content = Editor::new()
        .edit("作業内容を入力してください")
        .unwrap();
}
```

#### Ratatui（フルスクリーンTUI）
```rust
use ratatui::{
    backend::CrosstermBackend,
    widgets::{Block, Borders, List, ListItem},
    Terminal,
};

fn ui<B: Backend>(f: &mut Frame<B>, app: &App) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(50), Constraint::Percentage(50)])
        .split(f.size());
    
    // カレンダー表示
    let calendar = Calendar::new(app.selected_date)
        .block(Block::default().borders(Borders::ALL).title("日付選択"));
    f.render_widget(calendar, chunks[0]);
}
```

## 機能比較表

| 言語 | CLIフレームワーク | インタラクティブライブラリ | 日付選択 | 自動補完 | フルTUI |
|------|-------------------|--------------------------|----------|----------|---------|
| Python | Typer/Click | Rich+PromptKit/Questionary | ◎ | ◎ | ○ |
| Go | Cobra | Survey/BubbleTea | ◎ | ○ | ◎ |
| Node.js | Commander | Inquirer/Prompts | ◎ | ◎ | ○ |
| Rust | Clap | Dialoguer/Ratatui | ○ | ○ | ◎ |

## 日報入力のインタラクティブ実装例

### Python（Questionary）での実装
```python
import questionary
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table

console = Console()

def create_interactive_report():
    # 1. 日付選択（カーソルキーで選択）
    dates = []
    for i in range(7):
        date = datetime.now() - timedelta(days=i)
        dates.append({
            'name': date.strftime('%Y-%m-%d (%a)') + (' ← 今日' if i == 0 else ''),
            'value': date.strftime('%Y-%m-%d')
        })
    
    selected_date = questionary.select(
        "日付を選択してください（↑↓キーで移動、Enterで決定）:",
        choices=[d['name'] for d in dates]
    ).ask()
    
    # 2. プロジェクト選択（入力補完付き）
    project = questionary.autocomplete(
        'プロジェクト名:',
        choices=['ProjectA', 'ProjectB', 'ProjectC', 'その他'],
        meta_information={
            'ProjectA': '開発案件',
            'ProjectB': '保守案件',
            'ProjectC': '新規提案'
        }
    ).ask()
    
    # 3. 作業内容（複数選択）
    tasks = questionary.checkbox(
        '本日の作業内容を選択:',
        choices=[
            '設計',
            '実装',
            'コードレビュー',
            'テスト',
            'ドキュメント作成',
            '会議',
            'その他'
        ]
    ).ask()
    
    # 4. 詳細入力
    details = {}
    for task in tasks:
        detail = questionary.text(f'{task}の詳細:').ask()
        details[task] = detail
    
    # 5. 確認画面
    console.print("\n[bold]入力内容の確認[/bold]")
    table = Table(show_header=False)
    table.add_column("項目", style="cyan")
    table.add_column("内容")
    table.add_row("日付", selected_date)
    table.add_row("プロジェクト", project)
    for task, detail in details.items():
        table.add_row(f"  {task}", detail)
    
    console.print(table)
    
    if questionary.confirm('この内容で日報を作成しますか？').ask():
        return {
            'date': selected_date,
            'project': project,
            'tasks': details
        }
    else:
        return None
```

## 推奨構成

### 開発効率重視
**Python + Typer + Questionary/Rich**
- 最も豊富な機能
- 美しいUI
- 開発が簡単

### 配布重視
**Go + Cobra + Survey**
- 単一バイナリ
- 十分なインタラクティブ機能
- クロスプラットフォーム

### Web技術者向け
**Node.js + Commander + Inquirer**
- 慣れ親しんだエコシステム
- 豊富なプラグイン
- npmでの配布

### パフォーマンス重視
**Rust + Clap + Dialoguer**
- 最速
- メモリ効率的
- 学習コストが高い

## 結論

**インタラクティブ機能の実装難易度:**
```
Python = Node.js < Go < Rust
```

**推奨:**
1. **MVP開発**: Python + Questionary（最速で高機能）
2. **本番配布**: Go + Survey（バランスが良い）
3. **高度なTUI**: Go + BubbleTea または Rust + Ratatui

日報入力のようなインタラクティブなCLIには、Python（Questionary）またはNode.js（Inquirer）が最も適しています。配布を考慮する場合は、Go（Survey）が良いバランスを提供します。