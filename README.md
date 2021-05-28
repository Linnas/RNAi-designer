
# RNAi designer

## Project setup
```
npm install
npm run electron:serve
npm run electron:build
```

### Framework
vue + vue-cli + django + electronjs + vuetify

### Pipeline
1. Input target sequences into textarea or upload file
2. Find all possible siRNA sequence.
3. Align each candidate sequence with genome index using Bowtie
4. Test with RNAplfold.
5. Check efficiency of candidate sequence.
6. Output analysis.


### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
