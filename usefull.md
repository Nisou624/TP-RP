### Cheatcode Repo:
    https://github.com/UsmanJafri/PyconChat

### For CLI:
    import inquirer

    def main():
        questions = [
            inquirer.List('choice',
                          message='Select an option:',
                          choices=['Option A', 'Option B', 'Option C']),
        ]
    
        answers = inquirer.prompt(questions)
    
        selected_option = answers['choice']
        print(f'You selected: {selected_option}')
    
    if __name__ == '__main__':
        main()
 